# Script to generate 20 TikTok Pixel signatures

import yaml
from pathlib import Path

# TikTok Pixel events
tiktok_events = [
    ("ViewContent", 7.5, "free", "Content view tracking"),
    ("ClickButton", 7.0, "free", "Button click tracking"),
    ("Search", 7.5, "free", "Search event"),
    ("AddToCart", 8.5, "pro", "Cart addition"),
    ("InitiateCheckout", 8.5, "pro", "Checkout started"),
    ("AddPaymentInfo", 9.0, "pro", "Payment info added"),
    ("CompletePayment", 9.5, "pro", "Purchase completed"),
    ("PlaceAnOrder", 9.5, "pro", "Order placed"),
    ("Contact", 8.0, "pro", "Contact form"),
    ("SubmitForm", 8.0, "pro", "Form submission"),
    ("Subscribe", 8.5, "pro", "Subscription"),
    ("Download", 7.5, "free", "Download tracking"),
    ("AddToWishlist", 7.0, "free", "Wishlist addition"),
    ("CompleteRegistration", 8.5, "pro", "Registration completed"),
    ("ViewCategory", 7.0, "free", "Category browsing"),
    ("PageView", 7.5, "free", "Page view"),
    ("ViewProduct", 7.5, "free", "Product view"),
    ("StartTrial", 8.5, "god", "Trial started"),
    ("EnterBio", 8.0, "god", "Bio info entered"),
    ("ShareContent", 7.0, "free", "Content shared")
]

sig_dir = Path('tracker_shield/signatures/tiktok')
sig_dir.mkdir(parents=True, exist_ok=True)

for idx, (event, risk, tier, desc) in enumerate(tiktok_events, start=1):
    sig_id = f"TIKTOK_{idx:03d}"
    filename = f"tiktok_{idx:03d}_{event.lower()}.tsig"
    
    sig = {
        'id': sig_id,
        'version': 1,
        'name': f"TikTok Pixel - {event}",
        'company': 'ByteDance/TikTok',
        'category': 'advertising',
        'risk_score': risk,
        'tier': tier,
        'description': f"TikTok Pixel event: {desc}",
        'patterns': [
            {'type': 'domain', 'value': 'analytics.tiktok.com', 'required': True},
            {'type': 'path', 'value': '/api/v2/pixel/track', 'required': True}
        ],
        'evidence': [
            {'type': 'param', 'name': 'Event Type', 'key': 'event', 'pii': False},
            {'type': 'param', 'name': 'Pixel Code', 'key': 'pixel_code', 'pii': False},
            {'type': 'param', 'name': 'TikTok Click ID', 'key': 'ttclid', 'pii': True},
            {'type': 'param', 'name': 'Page URL', 'key': 'url', 'pii': True}
        ],
        'references': ['https://ads.tiktok.com/marketing_api/docs?id=1739585696931842'],
        'tags': ['tiktok', 'pixel', 'advertising', 'bytedance']
    }
    
    with open(sig_dir / filename, 'w') as f:
        yaml.dump(sig, f, default_flow_style=False, sort_keys=False)
    
    print(f"✅ Created {sig_id}: {event} ({tier})")

print(f"\n✅ TikTok signatures complete: 20 total")
