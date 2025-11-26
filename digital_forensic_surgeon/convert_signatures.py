"""
Convert TrackerShield signatures to browser extension JSON format
"""

import json
import yaml
from pathlib import Path

def convert_signatures_to_json():
    """Convert TrackerShield signatures to browser-friendly JSON"""
    
    # Use the compiled signature database instead
    from tracker_shield.compiler.sig_compiler import SignatureCompiler
    
    output_file = Path('extension/signatures.json')
    
    compiler = SignatureCompiler()
    
    # Load from compiled databases
    all_signatures = []
    
    # Load God tier (all 180 signatures)
    god_db_path = Path('tracker_shield/data/tracker_shield_god.tsdb')
    if god_db_path.exists():
        signatures = compiler.load_database(god_db_path)
        
        for sig in signatures:
            # Convert pattern objects to strings
            pattern_strings = []
            for pattern in sig.patterns[:3]:  # First 3 patterns
                if hasattr(pattern, 'pattern'):
                    # It's a compiled regex
                    pattern_strings.append(pattern.pattern)
                else:
                    # It's already a string
                    pattern_strings.append(str(pattern))
            
            all_signatures.append({
                'id': sig.id,
                'name': sig.name,
                'company': sig.company,
                'category': sig.category,
                'risk_score': sig.risk_score,
                'patterns': [
                    {'type': 'contains', 'value': p}
                    for p in pattern_strings
                ]
            })
    
    # Save to JSON
    output_file.parent.mkdir(exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump({
            'version': '1.0',
            'total': len(all_signatures),
            'signatures': all_signatures
        }, f, indent=2)
    
    print(f"✅ Converted {len(all_signatures)} signatures to {output_file}")
    
    # Summary
    by_company = {}
    for sig in all_signatures:
        company = sig['company']
        by_company[company] = by_company.get(company, 0) + 1
    
    print(f"\n📊 Summary:")
    for company, count in sorted(by_company.items(), key=lambda x: x[1], reverse=True):
        print(f"   {company}: {count} signatures")

if __name__ == '__main__':
    convert_signatures_to_json()
