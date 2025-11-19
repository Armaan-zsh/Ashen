"""OSINT scanner for Digital Forensic Surgeon - Phase 3: Sherlock."""

from __future__ import annotations

import re
import time
import requests
from urllib.parse import quote
from pathlib import Path
from typing import Dict, List, Any, Optional, Generator, Set
from datetime import datetime
from dataclasses import dataclass
import json

from digital_forensic_surgeon.core.models import EvidenceItem
from digital_forensic_surgeon.core.exceptions import ScannerError
from digital_forensic_surgeon.utils.concurrency import run_parallel_tasks


@dataclass
class OSINTSite:
    """Represents a target site for username enumeration."""
    name: str
    url_template: str
    check_type: str  # 'status_code', 'content_string', 'json_response'
    success_patterns: List[str]
    failure_patterns: List[str]
    category: str  # 'Social', 'Dev', 'Adult', 'Crypto', 'Gaming'
    priority: int = 1  # 1=high, 2=medium, 3=low
    rate_limit: float = 1.0  # seconds between requests


class OSINTScanner:
    """Open Source Intelligence scanner - enumerates usernames across platforms."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        # Load target sites
        self.target_sites = self._get_target_sites()
        
        # Results cache to avoid duplicate checks
        self.results_cache: Dict[str, Dict[str, Any]] = {}
    
    def scan_username(self, username: str) -> Generator[EvidenceItem, None, None]:
        """Scan a username across all target platforms."""
        if not username or len(username) < 3:
            return
        
        # Clean username
        clean_username = re.sub(r'[^a-zA-Z0-9._-]', '', username).lower()
        
        # Check cache first
        if clean_username in self.results_cache:
            cached_results = self.results_cache[clean_username]
            for result in cached_results.get('evidence_items', []):
                yield result
            return
        
        print(f"🔍 Starting OSINT scan for username: {clean_username}")
        
        # Create scan tasks for parallel execution
        tasks = []
        for site in self.target_sites:
            task = {
                'site': site,
                'username': clean_username,
                'function': self._check_site_parallel
            }
            tasks.append(task)
        
        # Run parallel checks
        results = []
        try:
            parallel_results = run_parallel_tasks(tasks, max_workers=self.config.get('osint_max_workers', 20))
            
            for result in parallel_results:
                if result and result.get('success'):
                    results.append(result)
                    
                    # Create evidence item for positive matches
                    evidence = EvidenceItem(
                        type="osint_match",
                        source="osint",
                        path=f"Username: {clean_username} on {result['site_name']}",
                        content=f"Username '{clean_username}' found on {result['site_name']}",
                        metadata={
                            "username": clean_username,
                            "site_name": result['site_name'],
                            "site_url": result['url'],
                            "category": result['category'],
                            "confidence": result.get('confidence', 0.8),
                            "found_at": datetime.now().isoformat(),
                            "response_data": result.get('response_data', {})
                        },
                        is_sensitive=True,
                        confidence=result.get('confidence', 0.8)
                    )
                    
                    yield evidence
        
        except Exception as e:
            yield EvidenceItem(
                type="osint_scan_error",
                source="osint",
                path="osint_scan",
                content=f"OSINT scan failed: {e}",
                is_sensitive=False,
                confidence=0.1
            )
        
        # Cache results
        self.results_cache[clean_username] = {
            'timestamp': datetime.now().isoformat(),
            'total_sites_checked': len(self.target_sites),
            'matches_found': len(results),
            'evidence_items': list(results)  # Convert generator to list
        }
    
    def _get_target_sites(self) -> List[OSINTSite]:
        """Get list of target sites for username enumeration."""
        sites = [
            # High Priority Social Platforms
            OSINTSite("GitHub", "https://github.com/{username}", "status_code", 
                     ["200"], ["404", "Not Found"], "Dev", 1, 0.5),
            OSINTSite("Reddit", "https://www.reddit.com/user/{username}", "content_string", 
                     ["User page"], ["User not found", "404"], "Social", 1, 1.0),
            OSINTSite("Twitter", "https://twitter.com/{username}", "content_string", 
                     ["@timeline"], ["This account doesn\\'t exist"], "Social", 1, 1.0),
            OSINTSite("Instagram", "https://www.instagram.com/{username}/", "status_code", 
                     ["200"], ["Page Not Found", "404"], "Social", 1, 1.0),
            OSINTSite("LinkedIn", "https://www.linkedin.com/in/{username}/", "status_code", 
                     ["200"], ["Page Not Found"], "Social", 1, 1.0),
            OSINTSite("Facebook", "https://www.facebook.com/{username}", "status_code", 
                     ["200"], ["Page Not Found"], "Social", 1, 1.0),
            
            # Gaming Platforms
            OSINTSite("Steam", "https://steamcommunity.com/id/{username}", "status_code", 
                     ["200"], ["The specified profile could not be found"], "Gaming", 2, 1.0),
            OSINTSite("Twitch", "https://www.twitch.tv/{username}", "status_code", 
                     ["200"], ["Sorry, we couldn\\'t find that page"], "Gaming", 2, 1.0),
            OSINTSite("Roblox", "https://api.roblox.com/users/search?keyword={username}", "json_response", 
                     ["users"], [], "Gaming", 2, 0.8),
            
            # Adult Platforms (High Risk)
            OSINTSite("Pornhub", "https://www.pornhub.com/users/{username}", "status_code", 
                     ["200"], ["404 Not Found"], "Adult", 1, 2.0),
            OSINTSite("XVideos", "https://www.xvideos.com/pornstar/{username}", "status_code", 
                     ["200"], ["404"], "Adult", 1, 2.0),
            
            # Crypto & Finance
            OSINTSite("Coinbase", "https://www.coinbase.com/{username}", "status_code", 
                     ["200"], ["404"], "Crypto", 2, 1.0),
            OSINTSite("Binance", "https://www.binance.com/en/user/{username}", "status_code", 
                     ["200"], ["404"], "Crypto", 2, 1.0),
            
            # Dev Platforms
            OSINTSite("Stack Overflow", "https://stackoverflow.com/users/{username}", "status_code", 
                     ["200"], ["Page Not Found"], "Dev", 2, 1.0),
            OSINTSite("CodePen", "https://codepen.io/{username}", "status_code", 
                     ["200"], ["404"], "Dev", 2, 1.0),
            OSINTSite("Replit", "https://replit.com/@{username}", "status_code", 
                     ["200"], ["404"], "Dev", 2, 1.0),
            OSINTSite("GitLab", "https://gitlab.com/{username}", "status_code", 
                     ["200"], ["404"], "Dev", 2, 1.0),
            OSINTSite("Bitbucket", "https://bitbucket.org/{username}", "status_code", 
                     ["200"], ["Repository not found"], "Dev", 2, 1.0),
            
            # Music & Content
            OSINTSite("YouTube", "https://www.youtube.com/@{username}", "status_code", 
                     ["200"], ["This channel doesn't exist"], "Social", 2, 1.0),
            OSINTSite("TikTok", "https://www.tiktok.com/@{username}", "status_code", 
                     ["200"], ["Couldn't find this account"], "Social", 2, 1.0),
            OSINTSite("SoundCloud", "https://soundcloud.com/{username}", "status_code", 
                     ["200"], ["404 - Not Found"], "Social", 2, 1.0),
            OSINTSite("Medium", "https://medium.com/@{username}", "content_string", 
                     ["Stories by"], ["404"], "Social", 2, 1.0),
            OSINTSite("DeviantArt", "https://www.deviantart.com/{username}", "status_code", 
                     ["200"], ["The page you are looking for can't be found"], "Social", 2, 1.0),
            
            # Forums & Communities
            OSINTSite("Hacker News", "https://news.ycombinator.com/user?id={username}", "content_string", 
                     ["karma", "submissions"], ["No such user"], "Dev", 3, 1.0),
            OSINTSite("Quora", "https://www.quora.com/profile/{username}", "status_code", 
                     ["200"], ["404"], "Social", 3, 1.0),
            
            # Additional Social
            OSINTSite("Pinterest", "https://www.pinterest.com/{username}/", "status_code", 
                     ["200"], ["Oops, we couldn't find that page"], "Social", 3, 1.0),
            OSINTSite("Snapchat", "https://www.snapchat.com/add/{username}", "status_code", 
                     ["200"], ["Couldn't find that username"], "Social", 3, 2.0),
            OSINTSite("Discord", "https://discord.com/users/{username}", "status_code", 
                     ["200"], ["Unknown User"], "Social", 3, 1.0),
            
            # Professional & Business
            OSINTSite("Behance", "https://www.behance.net/{username}", "status_code", 
                     ["200"], ["Page Not Found"], "Social", 3, 1.0),
            OSINTSite("Dribbble", "https://dribbble.com/{username}", "status_code", 
                     ["200"], ["404"], "Social", 3, 1.0),
            
            # Dating & Lifestyle
            OSINTSite("Tinder", "https://www.gotinder.com/@{username}", "status_code", 
                     ["200"], ["404"], "Social", 3, 2.0),
            OSINTSite("OKCupid", "https://www.okcupid.com/profile/{username}", "status_code", 
                     ["200"], ["Page not found"], "Social", 3, 2.0),
        ]
        
        return sorted(sites, key=lambda x: (x.priority, x.rate_limit))
    
    def _check_site_parallel(self, site: OSINTSite, username: str) -> Optional[Dict[str, Any]]:
        """Check a single site (for parallel execution)."""
        try:
            return self._check_site(site, username)
        except Exception as e:
            return None
    
    def _check_site(self, site: OSINTSite, username: str) -> Optional[Dict[str, Any]]:
        """Check if username exists on a specific site."""
        try:
            # Format URL
            url = site.url_template.format(username=quote(username))
            
            # Add rate limiting
            time.sleep(site.rate_limit)
            
            # Make request
            response = self.session.get(
                url, 
                timeout=self.config.get('osint_timeout', 10),
                allow_redirects=False
            )
            
            # Analyze response
            result = self._analyze_response(site, response, url, username)
            
            if result and result.get('success'):
                return result
            
            return None
            
        except requests.exceptions.Timeout:
            return None
        except requests.exceptions.RequestException:
            return None
        except Exception:
            return None
    
    def _analyze_response(self, site: OSINTSite, response, url: str, username: str) -> Optional[Dict[str, Any]]:
        """Analyze response to determine if username exists."""
        try:
            success = False
            confidence = 0.5
            
            if site.check_type == "status_code":
                success = response.status_code == 200
                confidence = 0.9 if success else 0.1
            
            elif site.check_type == "content_string":
                if response.status_code == 200:
                    content = response.text.lower()
                    # Check for failure patterns first
                    if any(pattern.lower() in content for pattern in site.failure_patterns):
                        success = False
                        confidence = 0.1
                    # Check for success patterns
                    elif any(pattern.lower() in content for pattern in site.success_patterns):
                        success = True
                        confidence = 0.8
                    else:
                        # Default to failure if no clear indicators
                        success = False
                        confidence = 0.3
            
            elif site.check_type == "json_response":
                if response.status_code == 200:
                    try:
                        data = response.json()
                        # Check for success indicators in JSON
                        if isinstance(data, dict) and any(key in data for key in site.success_patterns):
                            success = True
                            confidence = 0.8
                        elif isinstance(data, list) and len(data) > 0:
                            success = True
                            confidence = 0.7
                    except json.JSONDecodeError:
                        success = False
                        confidence = 0.2
            
            if success:
                return {
                    'success': True,
                    'site_name': site.name,
                    'url': url,
                    'category': site.category,
                    'confidence': confidence,
                    'status_code': response.status_code,
                    'response_data': {
                        'content_length': len(response.text) if response.text else 0,
                        'final_url': response.url,
                        'response_time': response.elapsed.total_seconds()
                    }
                }
            
            return None
            
        except Exception:
            return None
    
    def get_scan_summary(self, evidence_items: List[EvidenceItem]) -> Dict[str, Any]:
        """Generate summary of OSINT scan results."""
        summary = {
            "total_matches": len(evidence_items),
            "categories_found": {},
            "highest_risk_matches": [],
            "social_platforms": 0,
            "dev_platforms": 0,
            "gaming_platforms": 0,
            "adult_platforms": 0,
            "crypto_platforms": 0
        }
        
        for item in evidence_items:
            if item.type == "osint_match":
                category = item.metadata.get("category", "Unknown")
                confidence = item.metadata.get("confidence", 0)
                
                # Count by category
                summary["categories_found"][category] = summary["categories_found"].get(category, 0) + 1
                
                # Count specific platform types
                if category == "Social":
                    summary["social_platforms"] += 1
                elif category == "Dev":
                    summary["dev_platforms"] += 1
                elif category == "Gaming":
                    summary["gaming_platforms"] += 1
                elif category == "Adult":
                    summary["adult_platforms"] += 1
                elif category == "Crypto":
                    summary["crypto_platforms"] += 1
                
                # High risk matches (adult sites + high confidence social)
                if category == "Adult" or confidence > 0.8:
                    summary["highest_risk_matches"].append({
                        "platform": item.metadata.get("site_name"),
                        "url": item.metadata.get("site_url"),
                        "category": category,
                        "confidence": confidence
                    })
        
        return summary