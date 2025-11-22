"""
Data Broker and Tracker Intelligence Database
Comprehensive database of known data brokers, tracking companies, and ad networks
"""

from typing import Dict, Any, List, Set, Optional
from dataclasses import dataclass, field
import json
from pathlib import Path


@dataclass
class TrackerEntity:
    """Represents a tracking entity/company"""
    name: str
    category: str  # Ad Network, Analytics, Data Broker, Social Tracking, Fingerprinting
    risk_score: float  # 0-10 scale
    domains: List[str] = field(default_factory=list)
    data_collected: List[str] = field(default_factory=list)
    practices: str = ""
    revenue_model: str = ""
    breach_history: List[Dict[str, Any]] = field(default_factory=list)
    known_for: str = ""


class DataBrokerDatabase:
    """Database of known data brokers and tracking entities"""
    
    def __init__(self):
        self.entities: Dict[str, TrackerEntity] = {}
        self.domain_to_entity: Dict[str, str] = {}
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize the database with known trackers and data brokers"""
        
        # Major Ad Networks
        self._add_entity(TrackerEntity(
            name="Google Advertising",
            category="Ad Network",
            risk_score=9.0,
            domains=[
                "doubleclick.net", "googleadservices.com", "googlesyndication.com",
                "googletagmanager.com", "google-analytics.com", "googletagservices.com",
                "2mdn.net", "admob.com", "adsense.google.com"
            ],
            data_collected=["browsing history", "search queries", "location", "demographics", "interests", "device info"],
            practices="Builds detailed profiles for targeted advertising across the web",
            revenue_model="Sells ad targeting and behavioral data",
            known_for="World's largest ad network, tracks 90%+ of web users"
        ))
        
        self._add_entity(TrackerEntity(
            name="Meta Platforms (Facebook)",
            category="Social Tracking",
            risk_score=9.5,
            domains=[
                "facebook.com", "facebook.net", "fbcdn.net", "connect.facebook.net",
                "facebook.com/tr", "facebook.com/plugins", "instagram.com"
            ],
            data_collected=["browsing history", "social connections", "interests", "location", "biometric data", "messages"],
            practices="Tracks users across the web via Facebook Pixel, even without accounts",
            revenue_model="Sells detailed user profiles to advertisers",
            known_for="Most aggressive cross-site tracker, shadow profiles",
            breach_history=[
                {"year": 2021, "records": "533M users", "type": "Personal data leak"},
                {"year": 2019, "records": "540M users", "type": "Cambridge Analytica"}
            ]
        ))
        
        self._add_entity(TrackerEntity(
            name="Amazon Advertising",
            category="Ad Network",
            risk_score=8.5,
            domains=[
                "amazon-adsystem.com", "cloudfront.net", "amazonaws.com",
                "amazon.com/gp/aw", "d3e2rdb7jxnb5h.cloudfront.net"
            ],
            data_collected=["purchase history", "browsing behavior", "search queries", "wishlists"],
            practices="Tracks shopping behavior and builds buyer profiles",
            revenue_model="Sells advertising and shopping insights",
            known_for="Fastest-growing ad platform, e-commerce tracking"
        ))
        
        # Analytics Companies
        self._add_entity(TrackerEntity(
            name="Google Analytics",
            category="Analytics",
            risk_score=8.0,
            domains=[
                "google-analytics.com", "analytics.google.com", "stats.g.doubleclick.net"
            ],
            data_collected=["page views", "session duration", "user flow", "demographics", "interests"],
            practices="Installed on 85%+ of websites, comprehensive user tracking",
            revenue_model="Data feeds into Google's ad network",
            known_for="Most popular analytics platform, cross-site tracking"
        ))
        
        self._add_entity(TrackerEntity(
            name="Mixpanel",
            category="Analytics",
            risk_score=7.5,
            domains=["mixpanel.com", "mxpnl.com"],
            data_collected=["user actions", "session replays", "funnel analysis", "A/B test data"],
            practices="Event-based analytics with detailed user journey tracking",
            revenue_model="Subscription analytics service",
            known_for="Detailed behavioral analytics, session replay"
        ))
        
        self._add_entity(TrackerEntity(
            name="Segment",
            category="Analytics",
            risk_score=7.0,
            domains=["segment.com", "segment.io"],
            data_collected=["user events", "customer data", "cross-platform behavior"],
            practices="Customer data platform aggregating data from multiple sources",
            revenue_model="Sells unified customer data access",
            known_for="Data aggregation hub for multiple analytics tools"
        ))
        
        self._add_entity(TrackerEntity(
            name="Hotjar",
            category="User Tracking",
            risk_score=8.5,
            domains=["hotjar.com", "hotjar.io"],
            data_collected=["mouse movements", "clicks", "scrolling", "form inputs", "session recordings"],
            practices="Records every action users take on websites",
            revenue_model="Sells session replay and heatmap services",
            known_for="Privacy-invasive session recording, captures keystrokes"
        ))
        
        self._add_entity(TrackerEntity(
            name="FullStory",
            category="User Tracking",
            risk_score=9.0,
            domains=["fullstory.com", "fullstory.io"],
            data_collected=["session recordings", "rage clicks", "error tracking", "form data"],
            practices="Captures complete user sessions including sensitive form inputs",
            revenue_model="Enterprise session replay platform",
            known_for="Extremely detailed session capture, can record passwords if misconfigured"
        ))
        
        # Data Brokers
        self._add_entity(TrackerEntity(
            name="Acxiom",
            category="Data Broker",
            risk_score=9.5,
            domains=["acxiom.com", "liveramp.com"],
            data_collected=["offline purchases", "financial data", "demographics", "medical history", "browsing history"],
            practices="One of largest data brokers, sells detailed consumer profiles",
            revenue_model="Sells data to marketers, financial institutions, government",
            known_for="4,000+ data points on 700M+ consumers"
        ))
        
        self._add_entity(TrackerEntity(
            name="Oracle BlueKai",
            category="Data Broker",
            risk_score=9.0,
            domains=["bluekai.com", "oracle.com/marketing"],
            data_collected=["browsing history", "purchase intent", "demographics", "interests"],
            practices="Third-party data marketplace selling audience segments",
            revenue_model="Data marketplace platform",
            known_for="Massive DMP with billions of profiles",
            breach_history=[
                {"year": 2019, "records": "Billions of records", "type": "Exposed consumer profiles"}
            ]
        ))
        
        self._add_entity(TrackerEntity(
            name="Epsilon",
            category="Data Broker",
            risk_score=8.5,
            domains=["epsilon.com", "conversantmedia.com"],
            data_collected=["email addresses", "purchase history", "loyalty programs", "demographics"],
            practices="Email and loyalty data aggregation",
            revenue_model="Data selling and marketing services",
            known_for="Largest permission-based email database",
            breach_history=[
                {"year": 2019, "records": "Unknown millions", "type": "Data breach"}
            ]
        ))
        
        # Ad Tech Companies
        self._add_entity(TrackerEntity(
            name="Criteo",
            category="Ad Network",
            risk_score=8.0,
            domains=["criteo.com", "criteo.net"],
            data_collected=["product views", "shopping cart data", "purchase history"],
            practices="Retargeting ads following users across the web",
            revenue_model="Programmatic ad retargeting",
            known_for="Aggressive retargeting, cart abandonment tracking"
        ))
        
        self._add_entity(TrackerEntity(
            name="AppNexus",
            category="Ad Network",
            risk_score=7.5,
            domains=["adnxs.com", "adnxs.net"],
            data_collected=["ad impressions", "clicks", "conversions", "audience segments"],
            practices="Real-time bidding platform",
            revenue_model="Ad exchange marketplace",
            known_for="Programmatic advertising platform"
        ))
        
        self._add_entity(TrackerEntity(
            name="Taboola",
            category="Ad Network",
            risk_score=7.0,
            domains=["taboola.com", "trc.taboola.com"],
            data_collected=["content interests", "engagement metrics", "click patterns"],
            practices="Content recommendation engine with tracking",
            revenue_model="Native advertising platform",
            known_for="'You may also like' widgets that track behavior"
        ))
        
        self._add_entity(TrackerEntity(
            name="Outbrain",
            category="Ad Network",
            risk_score=7.0,
            domains=["outbrain.com", "widgets.outbrain.com"],
            data_collected=["reading habits", "content preferences", "engagement"],
            practices="Content discovery platform with behavioral tracking",
            revenue_model="Native advertising",
            known_for="Recommended content widgets"
        ))
        
        # Fingerprinting & Advanced Tracking
        self._add_entity(TrackerEntity(
            name="Fingerprint.js / FingerprintJS",
            category="Fingerprinting",
            risk_score=9.0,
            domains=["fingerprintjs.com", "cdn.fpjs.io"],
            data_collected=["device fingerprints", "browser config", "canvas fingerprint", "WebGL"],
            practices="Creates unique device fingerprints to track users across sessions",
            revenue_model="Fingerprinting as a service",
            known_for="Advanced browser fingerprinting, bypasses cookie blockers"
        ))
        
        # Social & Other Trackers
        self._add_entity(TrackerEntity(
            name="Twitter Analytics",
            category="Social Tracking",
            risk_score=7.5,
            domains=["twitter.com/i/adsct", "analytics.twitter.com", "t.co"],
            data_collected=["tweet engagement", "interests", "followers"],
            practices="Tracks engagement and builds interest profiles",
            revenue_model="Advertising platform",
            known_for="Link shortener tracking (t.co)"
        ))
        
        self._add_entity(TrackerEntity(
            name="TikTok Pixel",
            category="Social Tracking",
            risk_score=8.5,
            domains=["tiktok.com/i18n/pixel", "analytics.tiktok.com"],
            data_collected=["video engagement", "browsing behavior", "demographics"],
            practices="Cross-site tracking for ad targeting",
            revenue_model="Advertising platform",
            known_for="Rapid growth in tracking presence"
        ))
        
        # Quantitative & Research
        self._add_entity(TrackerEntity(
            name="Quantcast",
            category="Analytics",
            risk_score=7.5,
            domains=["quantserve.com", "quantcast.com"],
            data_collected=["audience demographics", "site traffic", "user segments"],
            practices="Audience measurement and targeting",
            revenue_model="Advertising and measurement platform",
            known_for="Audience intelligence platform"
        ))
        
        self._add_entity(TrackerEntity(
            name="ScoreCard Research (Comscore)",
            category="Analytics",
            risk_score=7.0,
            domains=["scorecardresearch.com", "comscore.com"],
            data_collected=["browsing behavior", "demographics", "content consumption"],
            practices="Market research through tracking",
            revenue_model="Media measurement",
            known_for="One of oldest tracking networks"
        ))
        
        # CDNs (Often used for tracking)
        self._add_entity(TrackerEntity(
            name="Cloudflare",
            category="CDN/Security",
            risk_score=5.0,
            domains=["cloudflare.com", "cdnjs.cloudflare.com"],
            data_collected=["IP addresses", "traffic patterns", "bot detection"],
            practices="CDN and security service, sees all traffic",
            revenue_model="CDN and security services",
            known_for="Protects ~20% of web, but sees everything"
        ))
        
        # Additional tracking services
        self._add_entity(TrackerEntity(
            name="Optimizely",
            category="A/B Testing",
            risk_score=6.5,
            domains=["optimizely.com", "cdn.optimizely.com"],
            data_collected=["experiment participation", "conversion data", "user behavior"],
            practices="A/B testing with user segmentation",
            revenue_model="Experimentation platform",
            known_for="Widespread A/B testing platform"
        ))
        
        self._add_entity(TrackerEntity(
            name="Chartbeat",
            category="Analytics",
            risk_score=6.0,
            domains=["chartbeat.com", "static.chartbeat.com"],
            data_collected=["real-time engagement", "scroll depth", "attention time"],
            practices="Real-time content analytics",
            revenue_model="Publisher analytics",
            known_for="Real-time newsroom analytics"
        ))
    
    def _add_entity(self, entity: TrackerEntity):
        """Add an entity to the database and index its domains"""
        self.entities[entity.name] = entity
        for domain in entity.domains:
            self.domain_to_entity[domain.lower()] = entity.name
    
    def lookup_domain(self, domain: str) -> Optional[TrackerEntity]:
        """Look up a domain and return the associated tracker entity"""
        domain = domain.lower().strip()
        
        # Direct match
        if domain in self.domain_to_entity:
            entity_name = self.domain_to_entity[domain]
            return self.entities[entity_name]
        
        # Check if any tracked domain is in the given domain
        for tracked_domain, entity_name in self.domain_to_entity.items():
            if tracked_domain in domain or domain in tracked_domain:
                return self.entities[entity_name]
        
        return None
    
    def get_entity_by_name(self, name: str) -> Optional[TrackerEntity]:
        """Get entity by name"""
        return self.entities.get(name)
    
    def get_all_entities(self) -> List[TrackerEntity]:
        """Get all tracker entities"""
        return list(self.entities.values())
    
    def get_entities_by_category(self, category: str) -> List[TrackerEntity]:
        """Get all entities in a specific category"""
        return [e for e in self.entities.values() if e.category == category]
    
    def get_high_risk_entities(self, threshold: float = 8.0) -> List[TrackerEntity]:
        """Get all entities above a risk threshold"""
        return [e for e in self.entities.values() if e.risk_score >= threshold]
    
    def classify_url(self, url: str) -> Dict[str, Any]:
        """Classify a URL and return tracking information"""
        from urllib.parse import urlparse
        
        parsed = urlparse(url)
        domain = parsed.netloc
        
        entity = self.lookup_domain(domain)
        
        if entity:
            return {
                "is_tracker": True,
                "entity_name": entity.name,
                "category": entity.category,
                "risk_score": entity.risk_score,
                "data_collected": entity.data_collected,
                "known_for": entity.known_for
            }
        else:
            return {
                "is_tracker": False,
                "entity_name": "Unknown",
                "category": "Unknown",
                "risk_score": 0.0
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        return {
            "total_entities": len(self.entities),
            "total_domains": len(self.domain_to_entity),
            "categories": {
                category: len(self.get_entities_by_category(category))
                for category in set(e.category for e in self.entities.values())
            },
            "high_risk_count": len(self.get_high_risk_entities()),
            "average_risk_score": sum(e.risk_score for e in self.entities.values()) / len(self.entities)
        }
