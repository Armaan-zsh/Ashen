# Script to generate 30 Google Analytics signatures

import yaml
from pathlib import Path

# Google Analytics events (GA4 + Universal Analytics)
ga_events = [
    # GA4 Events (20)
    ("page_view", 7.5, "free", "google-analytics.com", "/g/collect", "GA4 page view"),
    ("click", 7.0, "free", "google-analytics.com", "/g/collect", "GA4 click event"),
    ("scroll", 6.5, "free", "google-analytics.com", "/g/collect", "GA4 scroll tracking"),
    ("view_item", 7.5, "free", "google-analytics.com", "/g/collect", "GA4 product view"),
    ("add_to_cart", 8.5, "pro", "google-analytics.com", "/g/collect", "GA4 cart addition"),
    ("purchase", 9.0, "pro", "google-analytics.com", "/g/collect", "GA4 purchase"),
    ("begin_checkout", 8.5, "pro", "google-analytics.com", "/g/collect", "GA4 checkout start"),
    ("add_payment_info", 9.0, "pro", "google-analytics.com", "/g/collect", "GA4 payment info"),
    ("add_shipping_info", 8.5, "pro", "google-analytics.com", "/g/collect", "GA4 shipping info"),
    ("generate_lead", 8.5, "pro", "google-analytics.com", "/g/collect", "GA4 lead generation"),
    ("login", 8.0, "pro", "google-analytics.com", "/g/collect", "GA4 user login"),
    ("sign_up", 8.5, "pro", "google-analytics.com", "/g/collect", "GA4 sign up"),
    ("search", 7.5, "free", "google-analytics.com", "/g/collect", "GA4 search"),
    ("select_content", 7.0, "free", "google-analytics.com", "/g/collect", "GA4 content selection"),
    ("share", 7.0, "free", "google-analytics.com", "/g/collect", "GA4 share"),
    ("video_start", 7.0, "free", "google-analytics.com", "/g/collect", "GA4 video play"),
    ("video_complete", 7.0, "free", "google-analytics.com", "/g/collect", "GA4 video completion"),
    ("view_promotion", 7.5, "pro", "google-analytics.com", "/g/collect", "GA4 promo view"),
    ("select_promotion", 7.5, "pro", "google-analytics.com", "/g/collect", "GA4 promo click"),
    ("session_start", 7.0, "free", "google-analytics.com", "/g/collect", "GA4 session begin"),
    
    # Universal Analytics (10)
    ("pageview", 7.5, "free", "google-analytics.com", "/collect", "UA pageview"),
    ("event", 7.0, "free", "google-analytics.com", "/collect", "UA event"),
    ("transaction", 9.0, "pro", "google-analytics.com", "/collect", "UA transaction"),
    ("item", 8.0, "pro", "google-analytics.com", "/collect", "UA item"),
    ("social", 7.0, "free", "google-analytics.com", "/collect", "UA social"),
    ("exception", 7.0, "free", "google-analytics.com", "/collect", "UA exception"),
    ("timing", 6.5, "free", "google-analytics.com", "/collect", "UA timing"),
    ("screenview", 7.0, "free", "google-analytics.com", "/collect", "UA screen view"),
    ("ecommerce", 8.5, "pro", "google-analytics.com", "/collect", "UA ecommerce"),
    ("enhanced_ecommerce", 9.0, "god", "google-analytics.com", "/collect", "UA enhanced ecommerce"),
]

sig_dir = Path('tracker_shield/signatures/google')
sig_dir.mkdir(parents=True, exist_ok=True)

for idx, (event, risk, tier, domain, path, desc) in enumerate(ga_events, start=2):  # Start at 2, we have GA4_001 already
    sig_id = f"GA4_{idx:03d}" if "/g/collect" in path else f"GA_UA_{idx:03d}"
    filename = f"ga_{idx:03d}_{event}.tsig"
    
    # Build signature
    sig = {
        'id': sig_id,
        'version': 1,
        'name': f"Google Analytics - {event}",
        'company': 'Google',
        'category': 'analytics',
        'risk_score': risk,
        'tier': tier,
        'description': f"{desc}",
        'patterns': [
            {'type': 'domain', 'value': domain, 'required': True},
            {'type': 'path', 'value': path, 'required': True},
            {'type': 'param_key', 'key': 'v' if 'UA' not in sig_id else 't', 'required': True}
        ],
        'evidence': [
            {'type': 'param', 'name': 'Event Name', 'key': 'en' if '/g/' in path else 't', 'pii': False},
            {'type': 'param', 'name': 'Client ID', 'key': 'cid', 'pii': True},
            {'type': 'param', 'name': 'Page URL', 'key': 'dl', 'pii': True},
            {'type': 'param', 'name': 'Measurement ID', 'key': 'tid', 'pii': False}
        ],
        'references': ['https://developers.google.com/analytics'],
        'tags': ['google', 'analytics', 'ga4' if '/g/' in path else 'universal-analytics']
    }
    
    # Add event-specific pattern
    if '/g/collect' in path:
        sig['patterns'].append({
            'type': 'param_value',
            'key': 'en',
            'value': event,
            'required': True
        })
    
    with open(sig_dir / filename, 'w') as f:
        yaml.dump(sig, f, default_flow_style=False, sort_keys=False)
    
    print(f"✅ Created {sig_id}: {event} ({tier})")

print(f"\n✅ Google Analytics signatures complete: 30 total")
