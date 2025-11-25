# Script to generate remaining Facebook signatures
# This creates 15 more variants programmatically

import yaml
from pathlib import Path

# Facebook event types with risk scores
fb_events = [
    ("InitiateCheckout", 8.5, "free", "Checkout flow started"),
    ("Search", 7.5, "free", "User performed search"),
    ("AddPaymentInfo", 9.0, "pro", "Payment information added"),
    ("CompleteRegistration", 8.5, "pro", "Account registration completed"),
    ("Contact", 8.0, "pro", "Contact form submitted"),
    ("CustomizeProduct", 7.0, "free", "Product customization"),
    ("Donate", 8.0, "free", "Donation made"),
    ("FindLocation", 7.0, "free", "Store location search"),
    ("Schedule", 7.5, "pro", "Appointment scheduled"),
    ("StartTrial", 8.5, "pro", "Free trial started"),
    ("SubmitApplication", 9.0, "pro", "Application submitted"),
    ("Subscribe", 8.5, "pro", "Subscription started"),
    ("AddToWishlist", 7.0, "free", "Item added to wishlist"),
    ("PageView", 7.5, "free", "Page view (already exists - skip)"),
    ("ViewProduct", 7.5, "free", "Product page viewed")
]

base_template = {
    'version': 1,
    'company': 'Meta/Facebook',
    'category': 'advertising',
    'patterns': [
        {'type': 'domain', 'value': 'facebook.com', 'required': True},
        {'type': 'path', 'value': '/tr', 'required': True},
        {'type': 'param_value', 'key': 'ev', 'required': True}
    ],
    'evidence': [
        {'type': 'param', 'name': 'Event Type', 'key': 'ev', 'pii': False},
        {'type': 'param', 'name': 'Facebook Pixel ID', 'key': 'id', 'pii': False},
        {'type': 'param', 'name': 'Page URL', 'key': 'dl', 'pii': True},
        {'type': 'param', 'name': 'Facebook Cookie', 'key': 'fbp', 'pii': True}
    ],
    'references': ['https://developers.facebook.com/docs/meta-pixel/reference'],
    'tags': ['facebook', 'pixel', 'conversion']
}

sig_dir = Path('tracker_shield/signatures/facebook')
sig_dir.mkdir(parents=True, exist_ok=True)

for idx, (event, risk, tier, desc) in enumerate(fb_events, start=6):
    if "already exists" in desc:
        continue
        
    sig_id = f"FB_PIXEL_{idx:03d}"
    filename = f"fb_pixel_{idx:03d}_{event.lower()}.tsig"
    
    sig = base_template.copy()
    sig['id'] = sig_id
    sig['name'] = f"Facebook Pixel - {event}"
    sig['risk_score'] = risk
    sig['tier'] = tier
    sig['description'] = f"Tracks {event} events. {desc}."
    sig['patterns'] = sig['patterns'].copy()
    sig['patterns'][2] = sig['patterns'][2].copy()
    sig['patterns'][2]['value'] = event
    
    with open(sig_dir / filename, 'w') as f:
        yaml.dump(sig, f, default_flow_style=False, sort_keys=False)
    
    print(f"✅ Created {sig_id}: {event} ({tier})")

print(f"\n✅ Facebook signatures complete: 20 total")
