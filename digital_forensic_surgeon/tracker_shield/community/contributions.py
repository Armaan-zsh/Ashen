"""
Community Contribution System
Anonymously upload unknown trackers to help grow the database
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional

class ContributionQueue:
    """Manages local queue of contributions"""
    
    def __init__(self, queue_file: Path = None):
        if queue_file is None:
            queue_file = Path.home() / ".trackershield" / "contributions.json"
        
        self.queue_file = queue_file
        self.queue_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing queue
        self.queue = self._load_queue()
    
    def _load_queue(self) -> List[Dict]:
        """Load contribution queue from disk"""
        if not self.queue_file.exists():
            return []
        
        try:
            with open(self.queue_file, 'r') as f:
                return json.load(f)
        except:
            return []
    
    def _save_queue(self):
        """Save queue to disk"""
        with open(self.queue_file, 'w') as f:
            json.dump(self.queue, f, indent=2)
    
    def add_unknown(self, detection: Dict) -> str:
        """
        Add unknown tracker to queue
        
        Args:
            detection: Detection result from UnknownPayloadDetector
        
        Returns:
            Hash of the contribution
        """
        
        # Strip ALL PII before storing
        anonymized = self._strip_pii(detection)
        
        # Hash for deduplication
        contrib_hash = self._hash_contribution(anonymized)
        
        # Check if already in queue
        if any(c['hash'] == contrib_hash for c in self.queue):
            return contrib_hash  # Already queued
        
        # Add to queue
        contribution = {
            'hash': contrib_hash,
            'data': anonymized,
            'timestamp': datetime.now().isoformat(),
            'score': detection.get('score', 0),
            'confidence': detection.get('confidence', 0)
        }
        
        self.queue.append(contribution)
        self._save_queue()
        
        return contrib_hash
    
    def _strip_pii(self, detection: Dict) -> Dict:
        """Strip ALL personally identifiable information"""
        
        # Only keep pattern data, NOT actual values
        return {
            'domain': self._anonymize_domain(detection.get('domain', '')),
            'path_pattern': self._get_path_pattern(detection.get('path', '')),
            'param_count': detection.get('param_count', 0),
            'reasons': detection.get('reasons', []),
            'score': detection.get('score', 0)
        }
    
    def _anonymize_domain(self, domain: str) -> str:
        """Keep only the tracking-relevant part of domain"""
        # Example: "tracking.example.com" -> "tracking.*.com"
        parts = domain.split('.')
        if len(parts) >= 3:
            return f"{parts[0]}.*.{parts[-1]}"
        return domain
    
    def _get_path_pattern(self, path: str) -> str:
        """Extract path pattern without specific IDs"""
        # Example: "/track/12345/event" -> "/track/*/event"
        import re
        # Replace numbers with *
        pattern = re.sub(r'\d+', '*', path)
        # Replace UUIDs with *
        pattern = re.sub(r'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}', '*', pattern)
        return pattern
    
    def _hash_contribution(self, data: Dict) -> str:
        """Generate hash for deduplication"""
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    def get_pending_count(self) -> int:
        """Get number of pending contributions"""
        return len(self.queue)
    
    def get_upload_bundle(self, max_size_kb: int = 100) -> Optional[Dict]:
        """
        Get bundle of contributions to upload
        
        Args:
            max_size_kb: Maximum bundle size in KB
        
        Returns:
            Bundle ready for upload, or None if empty
        """
        
        if not self.queue:
            return None
        
        # Build bundle
        bundle = {
            'version': 1,
            'timestamp': datetime.now().isoformat(),
            'contributions': []
        }
        
        current_size = 0
        max_bytes = max_size_kb * 1024
        
        for contrib in self.queue:
            contrib_size = len(json.dumps(contrib).encode())
            
            if current_size + contrib_size > max_bytes:
                break
            
            bundle['contributions'].append(contrib)
            current_size += contrib_size
        
        return bundle if bundle['contributions'] else None
    
    def mark_uploaded(self, contribution_hashes: List[str]):
        """Remove uploaded contributions from queue"""
        self.queue = [c for c in self.queue if c['hash'] not in contribution_hashes]
        self._save_queue()
    
    def should_prompt_contribution(self) -> bool:
        """Check if we should prompt user to contribute"""
        
        # Prompt if:
        # 1. Have at least 10 contributions
        # 2. Haven't prompted in last 7 days
        
        if len(self.queue) < 10:
            return False
        
        # Check last prompt time
        last_prompt_file = self.queue_file.parent / "last_prompt.txt"
        
        if last_prompt_file.exists():
            try:
                with open(last_prompt_file, 'r') as f:
                    last_prompt = datetime.fromisoformat(f.read().strip())
                
                if datetime.now() - last_prompt < timedelta(days=7):
                    return False  # Too soon
            except:
                pass
        
        return True
    
    def mark_prompted(self):
        """Mark that we prompted the user"""
        last_prompt_file = self.queue_file.parent / "last_prompt.txt"
        with open(last_prompt_file, 'w') as f:
            f.write(datetime.now().isoformat())


# Mock uploader (replace with real backend later)
class AnonymousUploader:
    """Upload contributions anonymously"""
    
    def __init__(self, endpoint: str = None):
        self.endpoint = endpoint or "https://api.trackershield.io/v1/contribute"
    
    def upload(self, bundle: Dict) -> bool:
        """
        Upload contribution bundle
        
        In production, this would POST to backend.
        For now, just save locally for testing.
        """
        
        # For testing: save to local file
        upload_dir = Path.home() / ".trackershield" / "uploads"
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        upload_file = upload_dir / f"upload_{timestamp}.json"
        
        with open(upload_file, 'w') as f:
            json.dump(bundle, f, indent=2)
        
        print(f"✅ Uploaded {len(bundle['contributions'])} contributions")
        print(f"   Saved to: {upload_file}")
        
        return True


# Demo
if __name__ == '__main__':
    print("=" * 60)
    print("Community Contribution System Demo")
    print("=" * 60)
    
    # Create queue
    queue = ContributionQueue()
    
    # Simulate detecting unknown trackers
    detections = [
        {
            'domain': 'tracking.newsite.com',
            'path': '/pixel/track/12345',
            'param_count': 5,
            'score': 65,
            'confidence': 65,
            'reasons': ['Known tracker domain', 'Suspicious parameters']
        },
        {
            'domain': 'analytics.shop.com',
            'path': '/collect/event',
            'param_count': 8,
            'score': 70,
            'confidence': 70,
            'reasons': ['Tracking-related path', 'Large query string']
        }
    ]
    
    print(f"\n📥 Adding {len(detections)} unknown trackers...\n")
    
    for detection in detections:
        hash_id = queue.add_unknown(detection)
        print(f"✅ Added: {detection['domain']}")
        print(f"   Hash: {hash_id[:16]}...")
        print(f"   Score: {detection['score']}")
    
    print(f"\n📊 Pending contributions: {queue.get_pending_count()}")
    
    # Check if should prompt
    if queue.should_prompt_contribution():
        print(f"\n💬 Should prompt user to contribute!")
    else:
        print(f"\n⏰ Not yet time to prompt (need 10+ contributions)")
    
    # Get upload bundle
    bundle = queue.get_upload_bundle()
    
    if bundle:
        print(f"\n📤 Upload bundle ready:")
        print(f"   Contributions: {len(bundle['contributions'])}")
        print(f"   Size: {len(json.dumps(bundle)):,} bytes")
        
        # "Upload" it
        uploader = AnonymousUploader()
        success = uploader.upload(bundle)
        
        if success:
            # Mark as uploaded
            hashes = [c['hash'] for c in bundle['contributions']]
            queue.mark_uploaded(hashes)
            print(f"\n✅ Uploaded and cleared from queue")
            print(f"   Remaining: {queue.get_pending_count()}")
    
    print("\n" + "=" * 60)
