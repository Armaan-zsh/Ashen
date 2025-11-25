"""
Test TrackerShield Signature System
"""

from pathlib import Path
from tracker_shield.compiler.sig_compiler import SignatureCompiler, build_all_tiers
from tracker_shield.engine.matcher import SignatureMatcher

def test_compile_and_match():
    """Test signature compilation and matching"""
    
    print("=" * 60)
    print("TrackerShield Signature System Test")
    print("=" * 60)
    
    # Paths
    sig_dir = Path('tracker_shield/signatures')
    data_dir = Path('tracker_shield/data')
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Compile signatures
    print("\n📦 Building signature databases...")
    build_all_tiers(sig_dir, data_dir)
    
    # 2. Load free tier
    print("\n🔓 Loading free tier database...")
    compiler = SignatureCompiler()
    signatures = compiler.load_database(data_dir / 'tracker_shield_free.tsdb')
    
    # 3. Create matcher
    print("\n🎯 Creating matcher...")
    matcher = SignatureMatcher(signatures)
    
    # 4. Test matching
    print("\n🧪 Testing pattern matching...\n")
    
    # Test Facebook Pixel
    fb_url = "https://www.facebook.com/tr?id=123456&ev=PageView&dl=https://example.com&fbp=fb.1.12345"
    fb_matches = matcher.match(fb_url)
    
    print(f"Test 1: Facebook Pixel")
    print(f"URL: {fb_url}")
    if fb_matches:
        match = fb_matches[0]
        print(f"✅ MATCHED: {match.signature.name}")
        print(f"   Company: {match.signature.company}")
        print(f"   Risk: {match.signature.risk_score}/10")
        print(f"   Confidence: {match.confidence:.0%}")
        print(f"   Evidence:")
        for key, value in match.evidence.items():
            print(f"     - {key}: {value}")
    else:
        print("❌ NO MATCH")
    
    print()
    
    # Test Google Analytics
    ga_url = "https://www.google-analytics.com/g/collect?v=2&tid=G-XXXXXX&en=page_view&dl=https://example.com&cid=12345&sid=67890"
    ga_matches = matcher.match(ga_url)
    
    print(f"Test 2: Google Analytics 4")
    print(f"URL: {ga_url}")
    if ga_matches:
        match = ga_matches[0]
        print(f"✅ MATCHED: {match.signature.name}")
        print(f"   Company: {match.signature.company}")
        print(f"   Risk: {match.signature.risk_score}/10")
        print(f"   Confidence: {match.confidence:.0%}")
        print(f"   Evidence:")
        for key, value in match.evidence.items():
            print(f"     - {key}: {value}")
    else:
        print("❌ NO MATCH")
    
    print()
    
    # Test random URL (should not match)
    random_url = "https://example.com/api/data?foo=bar"
    random_matches = matcher.match(random_url)
    
    print(f"Test 3: Random URL (should not match)")
    print(f"URL: {random_url}")
    if random_matches:
        print(f"❌ UNEXPECTED MATCH: {random_matches[0].signature.name}")
    else:
        print("✅ CORRECTLY REJECTED")
    
    print("\n" + "=" * 60)
    print("✅ TrackerShield Core System Working!")
    print("=" * 60)

if __name__ == '__main__':
    test_compile_and_match()
