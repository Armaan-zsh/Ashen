"""
Convert TrackerShield signatures to browser extension JSON format - FIXED
"""

import json
from pathlib import Path
import re

def convert_signatures_to_json():
    """Convert TrackerShield signatures to browser-friendly JSON"""
    
    from tracker_shield.compiler.sig_compiler import SignatureCompiler
    
    output_file = Path('extension/signatures.json')
    
    compiler = SignatureCompiler()
    
    all_signatures = []
    
    # Load God tier (all 180 signatures)
    god_db_path = Path('tracker_shield/data/tracker_shield_god.tsdb')
    if god_db_path.exists():
        signatures = compiler.load_database(god_db_path)
        
        for sig in signatures:
            # Extract actual values from Pattern objects
            pattern_list = []
            for pattern in sig.patterns[:5]:  # First 5 patterns max
                # Extract the actual value from Pattern object string representation
                pattern_str = str(pattern)
                
                # Try to extract value using regex
                if "value='" in pattern_str:
                    match = re.search(r"value='([^']+)'", pattern_str)
                    if match:
                        actual_value = match.group(1)
                        pattern_list.append({
                            'type': 'contains',
                            'value': actual_value
                        })
            
            if pattern_list:  # Only add if we have patterns
                all_signatures.append({
                    'id': sig.id,
                    'name': sig.name,
                    'company': sig.company,
                    'category': sig.category,
                    'risk_score': sig.risk_score,
                    'patterns': pattern_list
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
    
    # Show sample
    if all_signatures:
        print(f"\n🔍 Sample pattern:")
        print(f"   {all_signatures[0]['patterns'][0]}")

if __name__ == '__main__':
    convert_signatures_to_json()
