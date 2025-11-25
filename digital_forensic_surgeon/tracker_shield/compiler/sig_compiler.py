"""
Signature Compiler
Converts .tsig YAML files → encrypted .tsdb binary database
"""

import yaml
import pickle
import gzip
from pathlib import Path
from typing import List, Dict
from cryptography.fernet import Fernet
import hashlib

from tracker_shield.core.signature import TrackerSignature

class SignatureCompiler:
    """Compiles YAML signatures into encrypted binary database"""
    
    def __init__(self, encryption_key: bytes = None):
        """
        Args:
            encryption_key: AES key for encryption (generated if None)
        """
        if encryption_key is None:
            # Default key (should be different for prod)
            encryption_key = self._generate_key("TrackerShield_2026_God_Tier")
        
        self.cipher = Fernet(encryption_key)
    
    def _generate_key(self, passphrase: str) -> bytes:
        """Generate Fernet key from passphrase"""
        key_material = hashlib.sha256(passphrase.encode()).digest()
        # Fernet requires base64-encoded 32-byte key
        from base64 import urlsafe_b64encode
        return urlsafe_b64encode(key_material)
    
    def compile_signature(self, yaml_path: Path) -> TrackerSignature:
        """Load and parse a single .tsig file"""
        with open(yaml_path, 'r') as f:
            data = yaml.safe_load(f)
        
        return TrackerSignature.from_dict(data)
    
    def compile_directory(self, sig_dir: Path, tier: str = 'free') -> List[TrackerSignature]:
        """Compile all .tsig files in directory for specific tier"""
        signatures = []
        
        for yaml_file in sig_dir.rglob('*.tsig'):
            sig = self.compile_signature(yaml_file)
            
            # Filter by tier
            if tier == 'free' and sig.tier in ['free']:
                signatures.append(sig)
            elif tier == 'pro' and sig.tier in ['free', 'pro']:
                signatures.append(sig)
            elif tier == 'god':  # God tier gets everything
                signatures.append(sig)
        
        print(f"✅ Compiled {len(signatures)} signatures for {tier} tier")
        return signatures
    
    def build_database(self, signatures: List[TrackerSignature], output_path: Path):
        """Build encrypted .tsdb database"""
        
        # Convert to serializable format
        sig_data = [sig.to_dict() for sig in signatures]
        
        # Pickle + compress
        pickled = pickle.dumps(sig_data)
        compressed = gzip.compress(pickled)
        
        # Encrypt
        encrypted = self.cipher.encrypt(compressed)
        
        # Write to file
        with open(output_path, 'wb') as f:
            f.write(encrypted)
        
        print(f"✅ Built database: {output_path} ({len(signatures)} signatures, {len(encrypted):,} bytes)")
    
    def load_database(self, db_path: Path) -> List[TrackerSignature]:
        """Load encrypted .tsdb database"""
        
        # Read encrypted file
        with open(db_path, 'rb') as f:
            encrypted = f.read()
        
        # Decrypt
        compressed = self.cipher.decrypt(encrypted)
        
        # Decompress
        pickled = gzip.decompress(compressed)
        
        # Unpickle
        sig_data = pickle.loads(pickled)
        
        # Convert to TrackerSignature objects
        signatures = [TrackerSignature.from_dict(data) for data in sig_data]
        
        print(f"✅ Loaded {len(signatures)} signatures from {db_path}")
        return signatures


def build_all_tiers(sig_dir: Path, output_dir: Path):
    """Build all three tier databases"""
    
    compiler = SignatureCompiler()
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Free tier (monthly updates)
    free_sigs = compiler.compile_directory(sig_dir, tier='free')
    compiler.build_database(free_sigs, output_dir / 'tracker_shield_free.tsdb')
    
    # Pro tier (daily updates)
    pro_sigs = compiler.compile_directory(sig_dir, tier='pro')
    compiler.build_database(pro_sigs, output_dir / 'tracker_shield_pro.tsdb')
    
    # God tier (daily + exclusive)
    god_sigs = compiler.compile_directory(sig_dir, tier='god')
    compiler.build_database(god_sigs, output_dir / 'tracker_shield_god.tsdb')
    
    print(f"\n📊 Summary:")
    print(f"Free: {len(free_sigs)} signatures")
    print(f"Pro:  {len(pro_sigs)} signatures")
    print(f"God:  {len(god_sigs)} signatures")


if __name__ == '__main__':
    # Example usage
    sig_dir = Path('tracker_shield/signatures')
    output_dir = Path('tracker_shield/data')
    
    build_all_tiers(sig_dir, output_dir)
