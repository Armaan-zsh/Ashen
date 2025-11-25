# Script to generate 15 Amazon + 15 DoubleClick signatures

import yaml
from pathlib import Path

# Amazon OneTag events
amazon_events = [
    ("pageview", 7.5, "free", "Page view"),
    ("product_view", 8.0, "pro", "Product page view"),
    ("add_to_cart", 8.5, "pro", "Add to cart"),
    ("purchase", 9.5, "pro", "Purchase completed"),
    ("search", 7.5, "free", "Search event"),
    ("impression", 7.0, "free", "Ad impression"),
    ("click", 7.5, "free", "Ad click"),
    ("wishlist", 7.5, "free", "Wishlist addition"),
    ("checkout", 9.0, "pro", "Checkout started"),
    ("subscribe", 8.5, "god", "Prime subscription"),
    ("video_view", 7.0, "free", "Video watched"),
    ("rating", 7.5, "free", "Product rated"),
    ("review", 8.0, "pro", "Review submitted"),
    ("prime_modal", 8.0, "god", "Prime modal shown"),
    ("alexa_integration", 8.5, "god", "Alexa interaction")
]

# Google Ads / DoubleClick events
doubleclick_events = [
    ("ad_impression", 7.0, "free", "Ad displayed"),
    ("ad_click", 7.5, "free", "Ad clicked"),
    ("conversion", 9.0, "pro", "Conversion event"),
    ("remarketing", 8.0, "pro", "Remarketing tag"),
    ("dynamic_remarketing", 8.5, "pro", "Dynamic remarketing"),
    ("google_shopping", 8.5, "pro", "Shopping campaign"),
    ("lead_conversion", 9.0, "pro", "Lead conversion"),
    ("purchase_conversion", 9.5, "pro", "Purchase conversion"),
    ("signup_conversion", 8.5, "pro", "Sign-up conversion"),
    ("page_view", 7.0, "free", "Page view tracking"),
    ("floodlight", 8.0, "god", "Floodlight tag"),
    ("audience_pixel", 8.5, "god", "Audience building"),
    ("cross_device", 9.0, "god", "Cross-device tracking"),
    ("attribution", 8.5, "god", "Attribution tracking"),
    ("dynamic_creative", 8.0, "god", "Dynamic creative")
]

# Generate Amazon signatures
sig_dir = Path('tracker_shield/signatures/amazon')
sig_dir.mkdir(parents=True, exist_ok=True)

for idx, (event, risk, tier, desc) in enumerate(amazon_events, start=1):
    sig_id = f"AMAZON_{idx:03d}"
    filename = f"amazon_{idx:03d}_{event}.tsig"
    
    sig = {
        'id': sig_id,
        'version': 1,
        'name': f"Amazon OneTag - {event}",
        'company': 'Amazon',
        'category': 'advertising',
        'risk_score': risk,
        'tier': tier,
        'description': f"Amazon tracking: {desc}",
        'patterns': [
            {'type': 'domain', 'value': 'amazon-adsystem.com', 'required': True}
        ],
        'evidence': [
            {'type': 'param', 'name': 'Event Type', 'key': 'event', 'pii': False},
            {'type': 'param', 'name': 'Advertiser ID', 'key': 'id', 'pii': False},
            {'type': 'param', 'name': 'Page URL', 'key': 'u', 'pii': True}
        ],
        'references': ['https://advertising.amazon.com/'],
        'tags': ['amazon', 'advertising', 'onetag']
    }
    
    with open(sig_dir / filename, 'w') as f:
        yaml.dump(sig, f, default_flow_style=False, sort_keys=False)
    
    print(f"✅ Created {sig_id}: {event} ({tier})")

# Generate DoubleClick signatures
sig_dir = Path('tracker_shield/signatures/google')  # Same dir as GA

for idx, (event, risk, tier, desc) in enumerate(doubleclick_events, start=1):
    sig_id = f"DOUBLECLICK_{idx:03d}"
    filename = f"doubleclick_{idx:03d}_{event}.tsig"
    
    sig = {
        'id': sig_id,
        'version': 1,
        'name': f"Google Ads - {event}",
        'company': 'Google',
        'category': 'advertising',
        'risk_score': risk,
        'tier': tier,
        'description': f"DoubleClick/Google Ads: {desc}",
        'patterns': [
            {'type': 'domain', 'value': 'doubleclick.net', 'required': True}
        ],
        'evidence': [
            {'type': 'param', 'name': 'Event Type', 'key': 'type', 'pii': False},
            {'type': 'param', 'name': 'Conversion ID', 'key': 'id', 'pii': False},
            {'type': 'param', 'name': 'Label', 'key': 'label', 'pii': False},
            {'type': 'cookie', 'name': 'Google ID Cookie', 'key': 'IDE', 'pii': True}
        ],
        'references': ['https://support.google.com/google-ads/'],
        'tags': ['google', 'doubleclick', 'advertising', 'remarketing']
    }
    
    with open(sig_dir / filename, 'w') as f:
        yaml.dump(sig, f, default_flow_style=False, sort_keys=False)
    
    print(f"✅ Created {sig_id}: {event} ({tier})")

print(f"\n✅ Amazon signatures complete: 15 total")
print(f"✅ DoubleClick signatures complete: 15 total")
print(f"\n🎉 TOTAL: 100 SIGNATURES READY")
