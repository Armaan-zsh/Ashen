"""
Test license generation and validation
Debug the issue
"""

from tracker_shield.license.validator import LicenseGenerator, License

print("Testing license system...")

# Generate a Pro key
pro_key = LicenseGenerator.generate_key("test@example.com", "pro", 12)
print(f"\nGenerated Pro Key: {pro_key}")

# Try to validate
license = LicenseGenerator.validate_key(pro_key)
print(f"Validation result: {license}")

if license:
    print(f"✅ VALID - Tier: {license.tier}")
else:
    print(f"❌ INVALID - Debugging...")
    
    # Debug the validation process
    parts = pro_key.split('-')
    print(f"\nKey parts: {parts}")
    print(f"Prefix: {parts[0]}")
    print(f"Body: {'-'.join(parts[1:])}")
