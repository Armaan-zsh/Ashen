"""
Advanced Destination Intelligence and Domain Analysis
Provides comprehensive analysis of network destinations, tracking domains, and data recipients
"""

import re
import json
import socket
import time
import requests
from typing import Dict, List, Any, Optional, Generator, Tuple, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from urllib.parse import urlparse
import logging

try:
    import dns.resolver
    DNS_AVAILABLE = True
except ImportError:
    DNS_AVAILABLE = False

try:
    import geoip2.database
    import geoip2.errors
    GEOIP_AVAILABLE = True
except ImportError:
    GEOIP_AVAILABLE = False

from ..core.models import EvidenceItem, ScannerType
from ..core.config import ForensicConfig
from .base import BaseScanner

@dataclass
class DestinationInfo:
    """Represents detailed information about a network destination"""
    domain: str
    ip_addresses: List[str]
    country: str
    organization: str
    category: str
    risk_level: str
    privacy_policy: str
    data_retention: str
    third_party_sharing: bool
    tracking_technologies: List[str]
    first_seen: datetime
    last_seen: datetime
    connection_count: int
    data_volume: int

@dataclass
class TrackingDomain:
    """Represents a tracking/advertising domain"""
    domain: str
    company: str
    tracking_type: str
    data_collected: List[str]
    purposes: List[str]
    opt_out_available: bool
    privacy_score: float
    prevalence: int

@dataclass
class DataFlowPath:
    """Represents a complete data flow path from source to destination"""
    source_app: str
    intermediate_domains: List[str]
    final_destination: str
    data_types: List[str]
    transmission_method: str
    encryption: bool
    risk_assessment: str
    total_hops: int

class DestinationIntelligence(BaseScanner):
    """Advanced destination intelligence and domain analysis"""
    
    def __init__(self, config: Optional[ForensicConfig] = None):
        super().__init__(ScannerType.NETWORK, config)
        self.tracking_domains = self._init_tracking_domains()
    
    def scan(self) -> Generator[EvidenceItem, None, None]:
        """Main scan method for destination intelligence."""
        # For demo, yield a test evidence item
        yield EvidenceItem(
            id="dest_intel_test",
            source="destination_intelligence",
            type="test",
            content="Destination intelligence initialized successfully",
            metadata={"test": True}
        )
        self.risky_destinations = self._init_risky_destinations()
        self.domain_categories = self._init_domain_categories()
        self.destination_cache = {}
        
    def _init_tracking_domains(self) -> Dict[str, TrackingDomain]:
        """Initialize known tracking and advertising domains"""
        return {
            'google-analytics.com': TrackingDomain(
                domain='google-analytics.com',
                company='Google LLC',
                tracking_type='analytics',
                data_collected=['page_views', 'user_sessions', 'demographics', 'behavior'],
                purposes=['analytics', 'marketing', 'personalization'],
                opt_out_available=True,
                privacy_score=6.0,
                prevalence=95
            ),
            'facebook.com': TrackingDomain(
                domain='facebook.com',
                company='Meta Platforms',
                tracking_type='social_tracking',
                data_collected=['social_graph', 'behavior', 'demographics', 'interests'],
                purposes=['social', 'advertising', 'analytics'],
                opt_out_available=True,
                privacy_score=4.0,
                prevalence=90
            ),
            'doubleclick.net': TrackingDomain(
                domain='doubleclick.net',
                company='Google LLC',
                tracking_type='advertising',
                data_collected=['ad_clicks', 'conversions', 'user_profiles'],
                purposes=['advertising', 'retargeting'],
                opt_out_available=True,
                privacy_score=3.0,
                prevalence=85
            ),
            'googletagmanager.com': TrackingDomain(
                domain='googletagmanager.com',
                company='Google LLC',
                tracking_type='tag_management',
                data_collected=['user_events', 'conversions', 'custom_data'],
                purposes=['analytics', 'marketing'],
                opt_out_available=True,
                privacy_score=5.0,
                prevalence=80
            ),
            'googleads.g.doubleclick.net': TrackingDomain(
                domain='googleads.g.doubleclick.net',
                company='Google LLC',
                tracking_type='advertising',
                data_collected=['ad_impressions', 'clicks', 'conversions'],
                purposes=['advertising', 'retargeting'],
                opt_out_available=True,
                privacy_score=3.0,
                prevalence=75
            ),
            'connect.facebook.net': TrackingDomain(
                domain='connect.facebook.net',
                company='Meta Platforms',
                tracking_type='social_tracking',
                data_collected=['social_interactions', 'page_data'],
                purposes=['social', 'analytics'],
                opt_out_available=True,
                privacy_score=4.0,
                prevalence=70
            ),
            'googleadservices.com': TrackingDomain(
                domain='googleadservices.com',
                company='Google LLC',
                tracking_type='advertising',
                data_collected=['ad_performance', 'conversion_data'],
                purposes=['advertising', 'analytics'],
                opt_out_available=True,
                privacy_score=4.0,
                prevalence=65
            ),
            'googlesyndication.com': TrackingDomain(
                domain='googlesyndication.com',
                company='Google LLC',
                tracking_type='ad_syndication',
                data_collected=['ad_requests', 'user_data'],
                purposes=['advertising', 'content_delivery'],
                opt_out_available=True,
                privacy_score=3.5,
                prevalence=60
            ),
            'amazonaws.com': TrackingDomain(
                domain='amazonaws.com',
                company='Amazon Web Services',
                tracking_type='cloud_hosting',
                data_collected=['usage_data', 'performance_metrics'],
                purposes=['hosting', 'analytics'],
                opt_out_available=False,
                privacy_score=7.0,
                prevalence=55
            ),
            'cloudflare.com': TrackingDomain(
                domain='cloudflare.com',
                company='Cloudflare Inc.',
                tracking_type='cdn_security',
                data_collected=['traffic_data', 'security_events'],
                purposes=['security', 'performance'],
                opt_out_available=True,
                privacy_score=8.0,
                prevalence=50
            ),
            'segment.io': TrackingDomain(
                domain='segment.io',
                company='Segment',
                tracking_type='data_collection',
                data_collected=['user_events', 'behavioral_data'],
                purposes=['analytics', 'marketing'],
                opt_out_available=True,
                privacy_score=5.5,
                prevalence=45
            ),
            'mixpanel.com': TrackingDomain(
                domain='mixpanel.com',
                company='Mixpanel',
                tracking_type='analytics',
                data_collected=['user_events', 'funnel_data'],
                purposes=['analytics', 'product_insights'],
                opt_out_available=True,
                privacy_score=6.0,
                prevalence=40
            ),
            'hotjar.com': TrackingDomain(
                domain='hotjar.com',
                company='Hotjar',
                tracking_type='user_experience',
                data_collected=['click_data', 'scroll_data', 'form_data'],
                purposes=['analytics', 'user_experience'],
                opt_out_available=True,
                privacy_score=5.0,
                prevalence=35
            ),
            'fullstory.com': TrackingDomain(
                domain='fullstory.com',
                company='FullStory',
                tracking_type='session_recording',
                data_collected=['user_sessions', 'click_data', 'form_data'],
                purposes=['analytics', 'user_experience'],
                opt_out_available=True,
                privacy_score=4.5,
                prevalence=30
            ),
            'optimizely.com': TrackingDomain(
                domain='optimizely.com',
                company='Optimizely',
                tracking_type='a_b_testing',
                data_collected=['experiment_data', 'user_variations'],
                purposes=['testing', 'personalization'],
                opt_out_available=True,
                privacy_score=6.5,
                prevalence=25
            ),
            'chartbeat.com': TrackingDomain(
                domain='chartbeat.com',
                company='Chartbeat',
                tracking_type='analytics',
                data_collected=['engagement_data', 'content_data'],
                purposes=['analytics', 'content_insights'],
                opt_out_available=True,
                privacy_score=6.0,
                prevalence=20
            ),
            'quantserve.com': TrackingDomain(
                domain='quantserve.com',
                company='Quantcast',
                tracking_type='audience_measurement',
                data_collected=['audience_data', 'demographics'],
                purposes=['advertising', 'analytics'],
                opt_out_available=True,
                privacy_score=4.0,
                prevalence=25
            ),
            'taboola.com': TrackingDomain(
                domain='taboola.com',
                company='Taboola',
                tracking_type='content_discovery',
                data_collected=['content_preferences', 'click_data'],
                purposes=['advertising', 'content'],
                opt_out_available=True,
                privacy_score=3.5,
                prevalence=30
            ),
            'outbrain.com': TrackingDomain(
                domain='outbrain.com',
                company='Outbrain',
                tracking_type='content_discovery',
                data_collected=['content_preferences', 'engagement_data'],
                purposes=['advertising', 'content'],
                opt_out_available=True,
                privacy_score=3.5,
                prevalence=25
            )
        }
    
    def _init_risky_destinations(self) -> Dict[str, Dict[str, Any]]:
        """Initialize known risky destinations with risk factors"""
        return {
            'data_brokers': {
                'domains': ['acxiom.com', 'experian.com', 'equifax.com', 'transunion.com', 'nielsen.com'],
                'risk_factors': ['data_collection', 'data_brokering', 'profiling'],
                'data_types': ['demographics', 'financial', 'behavioral', 'location'],
                'privacy_score': 2.0
            },
            'advertising_exchanges': {
                'domains': ['rubiconproject.com', 'pubmatic.com', 'indexww.com', 'criteo.com', 'adnxs.com'],
                'risk_factors': ['real_time_bidding', 'user_profiling', 'cross_site_tracking'],
                'data_types': ['browsing_history', 'interests', 'demographics'],
                'privacy_score': 2.5
            },
            'social_media_trackers': {
                'domains': ['facebook.com', 'instagram.com', 'twitter.com', 'linkedin.com', 'tiktok.com'],
                'risk_factors': ['social_graph', 'behavioral_tracking', 'profile_building'],
                'data_types': ['social_data', 'interests', 'connections', 'content'],
                'privacy_score': 3.0
            },
            'analytics_providers': {
                'domains': ['google-analytics.com', 'mixpanel.com', 'segment.io', 'amplitude.com', 'chartbeat.com'],
                'risk_factors': ['behavior_tracking', 'funnel_analysis', 'user_profiling'],
                'data_types': ['page_views', 'events', 'user_sessions', 'conversions'],
                'privacy_score': 4.0
            },
            'cloud_providers': {
                'domains': ['amazonaws.com', 'azure.microsoft.com', 'googlecloud.com', 'digitalocean.com'],
                'risk_factors': ['data_storage', 'processing', 'third_party_access'],
                'data_types': ['application_data', 'logs', 'user_content'],
                'privacy_score': 6.0
            }
        }
    
    def _init_domain_categories(self) -> Dict[str, List[str]]:
        """Initialize domain categories for classification"""
        return {
            'search_engines': ['google.com', 'bing.com', 'yahoo.com', 'duckduckgo.com', 'baidu.com'],
            'social_media': ['facebook.com', 'twitter.com', 'instagram.com', 'linkedin.com', 'tiktok.com', 'reddit.com'],
            'email_providers': ['gmail.com', 'outlook.com', 'yahoo.com', 'protonmail.com', 'icloud.com'],
            'streaming_services': ['netflix.com', 'youtube.com', 'hulu.com', 'disneyplus.com', 'primevideo.com'],
            'ecommerce': ['amazon.com', 'ebay.com', 'shopify.com', 'etsy.com', 'walmart.com'],
            'financial_services': ['paypal.com', 'stripe.com', 'square.com', 'chase.com', 'bankofamerica.com'],
            'cloud_storage': ['dropbox.com', 'googledrive.com', 'onedrive.com', 'icloud.com'],
            'productivity_tools': ['microsoft.com', 'google.com', 'slack.com', 'zoom.com', 'notion.so'],
            'news_media': ['cnn.com', 'bbc.com', 'reuters.com', 'nytimes.com', 'washingtonpost.com'],
            'gaming': ['steam.com', 'epicgames.com', 'twitch.tv', 'discord.com', 'roblox.com']
        }
    
    def analyze_destinations(self, destinations: List[str]) -> Generator[EvidenceItem, None, None]:
        """Analyze network destinations for intelligence"""
        try:
            for destination in destinations:
                destination_info = self._analyze_destination(destination)
                
                if destination_info:
                    yield EvidenceItem(
                        id=f"destination_{destination}_{int(time.time())}",
                        source="destination_intelligence",
                        data_type="destination_analysis",
                        description=f"Destination Analysis: {destination} ({destination_info.category}, {destination_info.risk_level} risk)",
                        severity=destination_info.risk_level,
                        metadata=asdict(destination_info)
                    )
                    
                    # Check if it's a tracking domain
                    if destination in self.tracking_domains:
                        tracking_info = self.tracking_domains[destination]
                        yield EvidenceItem(
                            id=f"tracking_domain_{destination}_{int(time.time())}",
                            source="destination_intelligence",
                            data_type="tracking_domain",
                            description=f"Tracking Domain: {destination} - {tracking_info.company} ({tracking_info.tracking_type})",
                            severity='medium' if tracking_info.privacy_score >= 5 else 'high',
                            metadata=asdict(tracking_info)
                        )
                    
                    # Check for risky destinations
                    for category, config in self.risky_destinations.items():
                        if destination in config['domains']:
                            yield EvidenceItem(
                                id=f"risky_destination_{destination}_{int(time.time())}",
                                source="destination_intelligence",
                                data_type="risky_destination",
                                description=f"Risky Destination: {destination} - {category}",
                                severity='high',
                                metadata={
                                    'domain': destination,
                                    'category': category,
                                    'risk_factors': config['risk_factors'],
                                    'data_types': config['data_types'],
                                    'privacy_score': config['privacy_score']
                                }
                            )
                            
        except Exception as e:
            yield EvidenceItem(
                id="destination_analysis_error",
                source="destination_intelligence",
                data_type="error",
                description=f"Error analyzing destinations: {str(e)}",
                severity="medium",
                metadata={"error": str(e)}
            )
    
    def _analyze_destination(self, destination: str) -> Optional[DestinationInfo]:
        """Analyze individual destination"""
        try:
            # Check cache first
            if destination in self.destination_cache:
                cached_info = self.destination_cache[destination]
                # Update last seen time
                cached_info.last_seen = datetime.now()
                cached_info.connection_count += 1
                return cached_info
            
            # Extract domain if destination is URL
            if destination.startswith(('http://', 'https://')):
                parsed = urlparse(destination)
                domain = parsed.netloc
            else:
                domain = destination
            
            # Get IP addresses
            ip_addresses = self._resolve_domain(domain)
            
            # Get geolocation and organization info
            country, organization = self._get_geolocation_info(ip_addresses[0] if ip_addresses else domain)
            
            # Determine category
            category = self._categorize_domain(domain)
            
            # Assess risk level
            risk_level = self._assess_destination_risk(domain, category, organization)
            
            # Get privacy information
            privacy_policy, data_retention, third_party_sharing = self._get_privacy_info(domain)
            
            # Identify tracking technologies
            tracking_technologies = self._identify_tracking_technologies(domain)
            
            destination_info = DestinationInfo(
                domain=domain,
                ip_addresses=ip_addresses,
                country=country,
                organization=organization,
                category=category,
                risk_level=risk_level,
                privacy_policy=privacy_policy,
                data_retention=data_retention,
                third_party_sharing=third_party_sharing,
                tracking_technologies=tracking_technologies,
                first_seen=datetime.now(),
                last_seen=datetime.now(),
                connection_count=1,
                data_volume=0
            )
            
            # Cache the result
            self.destination_cache[destination] = destination_info
            
            return destination_info
            
        except Exception as e:
            logging.error(f"Error analyzing destination {destination}: {str(e)}")
            return None
    
    def _resolve_domain(self, domain: str) -> List[str]:
        """Resolve domain to IP addresses"""
        try:
            if DNS_AVAILABLE:
                resolver = dns.resolver.Resolver()
                answers = resolver.resolve(domain, 'A')
                return [str(answer) for answer in answers]
            else:
                # Fallback to socket
                return [socket.gethostbyname(domain)]
        except:
            return []
    
    def _get_geolocation_info(self, ip_or_domain: str) -> Tuple[str, str]:
        """Get geolocation and organization information"""
        try:
            # This would typically use a GeoIP database
            # For now, return placeholder values
            if ip_or_domain.startswith(('192.168.', '10.', '127.')):
                return 'Local', 'Private Network'
            
            # Simple heuristic based on domain
            if '.com' in ip_or_domain:
                return 'Unknown', 'Commercial Entity'
            elif '.org' in ip_or_domain:
                return 'Unknown', 'Organization'
            elif '.gov' in ip_or_domain:
                return 'Unknown', 'Government'
            else:
                return 'Unknown', 'Unknown'
                
        except:
            return 'Unknown', 'Unknown'
    
    def _categorize_domain(self, domain: str) -> str:
        """Categorize domain based on known patterns"""
        domain_lower = domain.lower()
        
        for category, domains in self.domain_categories.items():
            for known_domain in domains:
                if known_domain in domain_lower or domain_lower in known_domain:
                    return category
        
        # Check tracking domains
        if domain in self.tracking_domains:
            return 'tracking_advertising'
        
        # Check risky destinations
        for category, config in self.risky_destinations.items():
            if domain in config['domains']:
                return category
        
        # Heuristic categorization
        if 'google' in domain_lower:
            return 'search_services'
        elif 'facebook' in domain_lower or 'meta' in domain_lower:
            return 'social_media'
        elif 'amazon' in domain_lower:
            return 'ecommerce'
        elif 'microsoft' in domain_lower or 'office' in domain_lower:
            return 'productivity_tools'
        elif 'netflix' in domain_lower or 'youtube' in domain_lower:
            return 'streaming_services'
        else:
            return 'unknown'
    
    def _assess_destination_risk(self, domain: str, category: str, organization: str) -> str:
        """Assess risk level of destination"""
        risk_score = 0
        
        # Known tracking domains
        if domain in self.tracking_domains:
            tracking_info = self.tracking_domains[domain]
            if tracking_info.privacy_score < 4:
                risk_score += 3
            elif tracking_info.privacy_score < 6:
                risk_score += 2
            else:
                risk_score += 1
        
        # Risky destination categories
        for category_name, config in self.risky_destinations.items():
            if domain in config['domains']:
                if config['privacy_score'] < 3:
                    risk_score += 4
                elif config['privacy_score'] < 4:
                    risk_score += 3
                else:
                    risk_score += 2
        
        # Category-based risk
        high_risk_categories = ['data_brokers', 'advertising_exchanges', 'social_media_trackers']
        medium_risk_categories = ['analytics_providers', 'unknown']
        
        if category in high_risk_categories:
            risk_score += 2
        elif category in medium_risk_categories:
            risk_score += 1
        
        # Organization-based risk
        if 'data' in organization.lower() or 'analytics' in organization.lower():
            risk_score += 1
        
        if risk_score >= 4:
            return 'critical'
        elif risk_score >= 3:
            return 'high'
        elif risk_score >= 2:
            return 'medium'
        else:
            return 'low'
    
    def _get_privacy_info(self, domain: str) -> Tuple[str, str, bool]:
        """Get privacy policy information"""
        # This would typically scrape privacy policies or use a database
        # For now, return placeholder values based on domain type
        
        if domain in self.tracking_domains:
            tracking_info = self.tracking_domains[domain]
            return (
                f"Privacy policy available for {tracking_info.company}",
                "30 days to 2 years",
                True  # Most tracking domains share data
            )
        
        # Heuristic based on domain category
        if 'google' in domain.lower():
            return ("Google Privacy Policy", "18-24 months", True)
        elif 'facebook' in domain.lower() or 'meta' in domain.lower():
            return ("Meta Privacy Policy", "Until account deletion", True)
        elif 'amazon' in domain.lower():
            return ("Amazon Privacy Policy", "Variable by service", True)
        else:
            return ("Privacy policy not analyzed", "Unknown", False)
    
    def _identify_tracking_technologies(self, domain: str) -> List[str]:
        """Identify tracking technologies used by domain"""
        technologies = []
        
        if domain in self.tracking_domains:
            tracking_info = self.tracking_domains[domain]
            technologies.append(tracking_info.tracking_type)
            
            # Add data collection methods
            if 'analytics' in tracking_info.tracking_type.lower():
                technologies.extend(['cookies', 'javascript', 'pixel_tracking'])
            elif 'advertising' in tracking_info.tracking_type.lower():
                technologies.extend(['cookies', 'real_time_bidding', 'pixel_tracking'])
            elif 'social' in tracking_info.tracking_type.lower():
                technologies.extend(['social_plugins', 'cookies', 'api_tracking'])
        
        # Common tracking technologies
        common_tech = ['google_analytics', 'facebook_pixel', 'doubleclick', 'adwords']
        for tech in common_tech:
            if tech.replace('_', '').replace('.', '') in domain.replace('.', '').replace('_', ''):
                technologies.append(tech)
        
        return list(set(technologies))
    
    def trace_data_flows(self, connections: List[Dict[str, Any]]) -> Generator[EvidenceItem, None, None]:
        """Trace complete data flow paths"""
        try:
            # Group connections by source application
            app_connections = {}
            for conn in connections:
                source_app = conn.get('process_name', 'unknown')
                if source_app not in app_connections:
                    app_connections[source_app] = []
                app_connections[source_app].append(conn)
            
            for app, conns in app_connections.items():
                # Trace data flow paths for each application
                data_paths = self._trace_application_data_paths(app, conns)
                
                for path in data_paths:
                    yield EvidenceItem(
                        id=f"data_flow_{app}_{hash(path.final_destination)}",
                        source="destination_intelligence",
                        data_type="data_flow_path",
                        description=f"Data Flow: {app} -> {path.final_destination} ({path.total_hops} hops)",
                        severity=path.risk_assessment,
                        metadata=asdict(path)
                    )
                    
        except Exception as e:
            yield EvidenceItem(
                id="data_flow_trace_error",
                source="destination_intelligence",
                data_type="error",
                description=f"Error tracing data flows: {str(e)}",
                severity="medium",
                metadata={"error": str(e)}
            )
    
    def _trace_application_data_paths(self, app: str, connections: List[Dict[str, Any]]) -> List[DataFlowPath]:
        """Trace data paths for a specific application"""
        paths = []
        
        for conn in connections:
            remote_addr = conn.get('remote_addr', '')
            remote_port = conn.get('remote_port', 0)
            
            # Get destination info
            destination_info = self._analyze_destination(remote_addr)
            
            if destination_info:
                # Determine if this is a direct or indirect connection
                intermediate_domains = []
                if destination_info.category in ['cdn', 'proxy', 'load_balancer']:
                    # This might be an intermediate destination
                    intermediate_domains.append(destination_info.domain)
                
                # Determine data types (based on port and domain)
                data_types = self._infer_data_types(remote_port, destination_info)
                
                # Determine transmission method
                transmission_method = self._determine_transmission_method(conn, destination_info)
                
                # Check encryption
                encryption = self._check_encryption(conn, destination_info)
                
                # Assess risk
                risk_assessment = self._assess_path_risk(app, destination_info, data_types, encryption)
                
                path = DataFlowPath(
                    source_app=app,
                    intermediate_domains=intermediate_domains,
                    final_destination=destination_info.domain,
                    data_types=data_types,
                    transmission_method=transmission_method,
                    encryption=encryption,
                    risk_assessment=risk_assessment,
                    total_hops=len(intermediate_domains) + 1
                )
                
                paths.append(path)
        
        return paths
    
    def _infer_data_types(self, port: int, destination: DestinationInfo) -> List[str]:
        """Infer data types based on port and destination"""
        data_types = []
        
        # Port-based inference
        if port == 443:
            data_types.append('encrypted_web_traffic')
        elif port == 80:
            data_types.append('web_traffic')
        elif port in [25, 587, 465]:
            data_types.append('email')
        elif port in [993, 995, 143, 110]:
            data_types.append('email_access')
        elif port in [21, 22, 23]:
            data_types.append('file_transfer')
        elif port == 53:
            data_types.append('dns_query')
        
        # Destination-based inference
        if destination.category == 'tracking_advertising':
            data_types.extend(['tracking_data', 'user_behavior'])
        elif destination.category == 'social_media':
            data_types.extend(['social_data', 'user_content'])
        elif destination.category == 'ecommerce':
            data_types.extend(['purchase_data', 'preferences'])
        elif destination.category == 'financial_services':
            data_types.extend(['financial_data', 'transactions'])
        
        return data_types
    
    def _determine_transmission_method(self, conn: Dict[str, Any], destination: DestinationInfo) -> str:
        """Determine transmission method"""
        protocol = conn.get('protocol', '').lower()
        
        if protocol == 'tcp':
            if conn.get('remote_port') == 443:
                return 'https'
            elif conn.get('remote_port') == 80:
                return 'http'
            else:
                return 'tcp_socket'
        elif protocol == 'udp':
            if conn.get('remote_port') == 53:
                return 'dns'
            else:
                return 'udp_socket'
        else:
            return 'unknown'
    
    def _check_encryption(self, conn: Dict[str, Any], destination: DestinationInfo) -> bool:
        """Check if connection is encrypted"""
        port = conn.get('remote_port', 0)
        protocol = conn.get('protocol', '').lower()
        
        # Common encrypted ports
        encrypted_ports = [443, 993, 995, 465, 636, 989, 990, 992]
        
        if port in encrypted_ports:
            return True
        
        # Check destination for known encryption
        if destination.domain in self.tracking_domains:
            tracking_info = self.tracking_domains[destination.domain]
            return 'https' in tracking_info.tracking_type.lower()
        
        return False
    
    def _assess_path_risk(self, app: str, destination: DestinationInfo, data_types: List[str], encryption: bool) -> str:
        """Assess risk of data flow path"""
        risk_score = 0
        
        # Application risk
        risky_apps = ['chrome.exe', 'firefox.exe', 'edge.exe', 'iexplore.exe']
        if app.lower() in risky_apps:
            risk_score += 1
        
        # Destination risk
        if destination.risk_level == 'critical':
            risk_score += 4
        elif destination.risk_level == 'high':
            risk_score += 3
        elif destination.risk_level == 'medium':
            risk_score += 2
        else:
            risk_score += 1
        
        # Data type risk
        sensitive_data_types = ['personal_info', 'financial_data', 'health_data', 'credentials']
        for data_type in data_types:
            if any(sensitive in data_type.lower() for sensitive in sensitive_data_types):
                risk_score += 2
        
        # Encryption factor
        if not encryption:
            risk_score += 2
        
        if risk_score >= 6:
            return 'critical'
        elif risk_score >= 4:
            return 'high'
        elif risk_score >= 2:
            return 'medium'
        else:
            return 'low'
    
    def generate_destination_report(self) -> Dict[str, Any]:
        """Generate comprehensive destination intelligence report"""
        report = {
            'summary': {
                'total_destinations': len(self.destination_cache),
                'high_risk_destinations': sum(1 for d in self.destination_cache.values() if d.risk_level in ['critical', 'high']),
                'tracking_domains': sum(1 for d in self.destination_cache.keys() if d in self.tracking_domains),
                'unique_countries': len(set(d.country for d in self.destination_cache.values())),
                'unique_organizations': len(set(d.organization for d in self.destination_cache.values()))
            },
            'top_destinations': self._get_top_destinations(),
            'risk_analysis': self._analyze_destination_risks(),
            'tracking_analysis': self._analyze_tracking_domains(),
            'geographic_distribution': self._analyze_geographic_distribution(),
            'recommendations': self._generate_destination_recommendations()
        }
        
        return report
    
    def _get_top_destinations(self) -> List[Dict[str, Any]]:
        """Get top destinations by connection count"""
        destinations = list(self.destination_cache.values())
        return sorted(
            [asdict(d) for d in destinations],
            key=lambda x: x['connection_count'],
            reverse=True
        )[:20]
    
    def _analyze_destination_risks(self) -> Dict[str, Any]:
        """Analyze destination security risks"""
        risks = {
            'critical_destinations': [],
            'high_risk_categories': {},
            'data_broker_connections': [],
            'unencrypted_connections': []
        }
        
        for dest in self.destination_cache.values():
            if dest.risk_level == 'critical':
                risks['critical_destinations'].append({
                    'domain': dest.domain,
                    'organization': dest.organization,
                    'country': dest.country,
                    'connection_count': dest.connection_count
                })
            
            # Count by category
            if dest.category not in risks['high_risk_categories']:
                risks['high_risk_categories'][dest.category] = 0
            risks['high_risk_categories'][dest.category] += 1
            
            # Check for data brokers
            for category, config in self.risky_destinations.items():
                if category == 'data_brokers' and dest.domain in config['domains']:
                    risks['data_broker_connections'].append(dest.domain)
        
        return risks
    
    def _analyze_tracking_domains(self) -> Dict[str, Any]:
        """Analyze tracking domain connections"""
        tracking_analysis = {
            'connected_trackers': [],
            'tracking_companies': {},
            'data_collection_types': set(),
            'privacy_scores': []
        }
        
        for dest in self.destination_cache.values():
            if dest.domain in self.tracking_domains:
                tracking_info = self.tracking_domains[dest.domain]
                
                tracking_analysis['connected_trackers'].append({
                    'domain': dest.domain,
                    'company': tracking_info.company,
                    'connection_count': dest.connection_count,
                    'privacy_score': tracking_info.privacy_score
                })
                
                # Count by company
                if tracking_info.company not in tracking_analysis['tracking_companies']:
                    tracking_analysis['tracking_companies'][tracking_info.company] = 0
                tracking_analysis['tracking_companies'][tracking_info.company] += 1
                
                # Collect data types
                tracking_analysis['data_collection_types'].update(tracking_info.data_collected)
                
                # Privacy scores
                tracking_analysis['privacy_scores'].append(tracking_info.privacy_score)
        
        tracking_analysis['data_collection_types'] = list(tracking_analysis['data_collection_types'])
        tracking_analysis['average_privacy_score'] = (
            sum(tracking_analysis['privacy_scores']) / len(tracking_analysis['privacy_scores'])
            if tracking_analysis['privacy_scores'] else 0
        )
        
        return tracking_analysis
    
    def _analyze_geographic_distribution(self) -> Dict[str, Any]:
        """Analyze geographic distribution of destinations"""
        geo_analysis = {
            'by_country': {},
            'by_organization': {},
            'high_risk_countries': []
        }
        
        for dest in self.destination_cache.values():
            # Count by country
            if dest.country not in geo_analysis['by_country']:
                geo_analysis['by_country'][dest.country] = 0
            geo_analysis['by_country'][dest.country] += 1
            
            # Count by organization
            if dest.organization not in geo_analysis['by_organization']:
                geo_analysis['by_organization'][dest.organization] = 0
            geo_analysis['by_organization'][dest.organization] += 1
            
            # High risk by country
            if dest.risk_level in ['critical', 'high']:
                if dest.country not in geo_analysis['high_risk_countries']:
                    geo_analysis['high_risk_countries'].append(dest.country)
        
        return geo_analysis
    
    def _generate_destination_recommendations(self) -> List[str]:
        """Generate security recommendations based on destination analysis"""
        recommendations = []
        
        high_risk_count = sum(1 for d in self.destination_cache.values() if d.risk_level in ['critical', 'high'])
        tracking_count = sum(1 for d in self.destination_cache.keys() if d in self.tracking_domains)
        
        if high_risk_count > 5:
            recommendations.append(f"High number of risky destinations ({high_risk_count}). Consider using firewall rules to block suspicious domains.")
        
        if tracking_count > 10:
            recommendations.append(f"Many tracking domains detected ({tracking_count}). Consider using privacy-focused browser extensions.")
        
        # Check for data brokers
        data_broker_connections = []
        for category, config in self.risky_destinations.items():
            if category == 'data_brokers':
                data_broker_connections.extend([d for d in self.destination_cache.keys() if d in config['domains']])
        
        if data_broker_connections:
            recommendations.append(f"Connections to data brokers detected: {', '.join(data_broker_connections[:3])}")
        
        # Geographic recommendations
        countries = set(d.country for d in self.destination_cache.values())
        if len(countries) > 10:
            recommendations.append("Data sent to many different countries. Consider regional data protection policies.")
        
        if not recommendations:
            recommendations.append("Destination analysis appears normal. Continue monitoring for new connections.")
        
        return recommendations

def scan_destination_intelligence(destinations: List[str] = None, config: Optional[ForensicConfig] = None) -> Dict[str, Any]:
    """Perform comprehensive destination intelligence analysis"""
    intelligence = DestinationIntelligence(config)
    
    results = {
        'destinations': [],
        'tracking_domains': [],
        'risky_destinations': [],
        'data_flows': [],
        'report': {}
    }
    
    if destinations:
        # Analyze destinations
        for evidence in intelligence.analyze_destinations(destinations):
            if evidence.data_type == 'destination_analysis':
                results['destinations'].append(asdict(evidence))
            elif evidence.data_type == 'tracking_domain':
                results['tracking_domains'].append(asdict(evidence))
            elif evidence.data_type == 'risky_destination':
                results['risky_destinations'].append(asdict(evidence))
    
    # Generate comprehensive report
    results['report'] = intelligence.generate_destination_report()
    
    return results
