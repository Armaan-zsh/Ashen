"""OSINT scanner for Digital Forensic Surgeon - Phase 3: Sherlock."""

from __future__ import annotations

import re
import time
import aiohttp
import asyncio
from urllib.parse import quote
from pathlib import Path
from typing import Dict, List, Any, Optional, Generator, Set, Union
from datetime import datetime
from dataclasses import dataclass
import json

from digital_forensic_surgeon.core.models import EvidenceItem
from digital_forensic_surgeon.core.exceptions import ScannerError


@dataclass
class OSINTSite:
    """Represents a target site for username enumeration."""
    name: str
    url_template: str
    check_type: str  # 'status_code', 'content_string', 'json_response'
    success_patterns: List[str]
    failure_patterns: List[str]
    category: str  # 'Social', 'Dev', 'Adult', 'Crypto', 'Gaming'
    priority: int = 1  # 1=high, 2=medium, 3=low
    rate_limit: float = 0.2  # seconds between requests


class AsyncOSINTScanner:
    def __init__(self, sites: List[OSINTSite], config: Union[Dict[str, Any], Any]):
        self.target_sites = sites
        self.config = config
        self.session_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

    async def _analyze_response(self, site: OSINTSite, response: aiohttp.ClientResponse, url: str, username: str) -> Optional[Dict[str, Any]]:
        """Analyze response to determine if username exists."""
        try:
            success = False
            confidence = 0.5
            
            if site.check_type == "status_code":
                success = response.status == 200
                confidence = 0.9 if success else 0.1
            
            elif site.check_type == "content_string":
                if response.status == 200:
                    content = (await response.text()).lower()
                    if any(pattern.lower() in content for pattern in site.failure_patterns):
                        success = False
                        confidence = 0.1
                    elif any(pattern.lower() in content for pattern in site.success_patterns):
                        success = True
                        confidence = 0.8
                    else:
                        success = False
                        confidence = 0.3
            
            elif site.check_type == "json_response":
                if response.status == 200:
                    try:
                        data = await response.json()
                        if isinstance(data, dict) and any(key in data for key in site.success_patterns):
                            success = True
                            confidence = 0.8
                        elif isinstance(data, list) and len(data) > 0:
                            success = True
                            confidence = 0.7
                    except json.JSONDecodeError:
                        success = False
                        confidence = 0.2
            
            if success:
                return {
                    'success': True,
                    'site_name': site.name,
                    'url': url,
                    'category': site.category,
                    'confidence': confidence,
                    'status_code': response.status,
                    'response_data': {
                        'content_length': response.content_length or 0,
                        'final_url': str(response.url),
                    }
                }
            
            return None
            
        except Exception:
            return None

    async def check_site(self, session: aiohttp.ClientSession, site: OSINTSite, username: str) -> Optional[Dict[str, Any]]:
        url = site.url_template.format(username=quote(username))
        try:
            await asyncio.sleep(site.rate_limit)
            # Handle both Dict and ForensicConfig objects
            timeout = self.config.get('osint_timeout', 10) if isinstance(self.config, dict) else getattr(self.config, 'osint_timeout', 10)
            async with session.get(url, timeout=timeout, allow_redirects=False) as response:
                return await self._analyze_response(site, response, url, username)
        except (asyncio.TimeoutError, aiohttp.ClientError):
            return None

    async def scan_all(self, username: str) -> List[Dict[str, Any]]:
        async with aiohttp.ClientSession(headers=self.session_headers) as session:
            tasks = [self.check_site(session, site, username) for site in self.target_sites]
            results = await asyncio.gather(*tasks)
            return [r for r in results if r is not None]


class OSINTScanner:
    """Open Source Intelligence scanner - enumerates username across platforms."""
    
    def __init__(self, config: Optional[Union[Dict[str, Any], Any]] = None):
        self.config = config or {}
        self.target_sites = self._get_target_sites()
        self.results_cache: Dict[str, Dict[str, Any]] = {}
        self.async_scanner = AsyncOSINTScanner(self.target_sites, self.config)
    
    async def scan_username_async(self, username: str) -> List[EvidenceItem]:
        """Scan a username across all target platforms asynchronously."""
        if not username or len(username) < 3:
            return []
        
        clean_username = re.sub(r'[^a-zA-Z0-9._-]', '', username).lower()
        
        if clean_username in self.results_cache:
            cached_results = self.results_cache[clean_username]
            return cached_results.get('evidence_items', [])
        
        print(f"[INFO] Starting OSINT scan for username: {clean_username}")
        
        try:
            results = await self.async_scanner.scan_all(clean_username)
            
            evidence_items = []
            for result in results:
                if result and result.get('success'):
                    evidence = EvidenceItem(
                        type="osint_match",
                        source="osint",
                        path=f"Username: {clean_username} on {result['site_name']}",
                        content=f"Username '{clean_username}' found on {result['site_name']}",
                        metadata={
                            "username": clean_username,
                            "site_name": result['site_name'],
                            "site_url": result['url'],
                            "category": result['category'],
                            "confidence": result.get('confidence', 0.8),
                            "found_at": datetime.now().isoformat(),
                            "response_data": result.get('response_data', {})
                        },
                        is_sensitive=True,
                        confidence=result.get('confidence', 0.8)
                    )
                    evidence_items.append(evidence)

            self.results_cache[clean_username] = {
                'timestamp': datetime.now().isoformat(),
                'total_sites_checked': len(self.target_sites),
                'matches_found': len(results),
                'evidence_items': evidence_items
            }
            
            return evidence_items

        except Exception as e:
            print(f"OSINT scan failed: {e}")
            return [EvidenceItem(
                type="osint_scan_error",
                source="osint",
                path="osint_scan",
                content=f"OSINT scan failed: {e}",
                is_sensitive=False,
                confidence=0.1
            )]

    def scan_username(self, username: str) -> Generator[EvidenceItem, None, None]:
        """Scan a username across all target platforms (Synchronous Wrapper)."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is running, we can't use run_until_complete.
                # This is a problem for sync wrappers called from async context.
                # But this method is intended for sync usage (CLI).
                # If called from async, use scan_username_async instead.
                raise RuntimeError("Cannot call sync scan_username from running event loop. Use scan_username_async.")
        except RuntimeError:
            # No loop running, create one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
        items = loop.run_until_complete(self.scan_username_async(username))
        for item in items:
            yield item
    
    def _get_target_sites(self) -> List[OSINTSite]:
        """Get list of target sites for username enumeration."""
        sites = [
            # High Priority Social Platforms
            OSINTSite("GitHub", "https://github.com/{username}", "status_code", 
                     ["200"], ["404", "Not Found"], "Dev", 1, 0.5),
            OSINTSite("Reddit", "https://www.reddit.com/user/{username}", "content_string", 
                     ["User page"], ["User not found", "404"], "Social", 1, 1.0),
            OSINTSite("Twitter", "https://twitter.com/{username}", "content_string", 
                     ["@timeline"], ["This account doesn\\'t exist"], "Social", 1, 1.0),
            OSINTSite("Instagram", "https://www.instagram.com/{username}/", "status_code", 
                     ["200"], ["Page Not Found", "404"], "Social", 1, 1.0),
            OSINTSite("LinkedIn", "https://www.linkedin.com/in/{username}/", "status_code", 
                     ["200"], ["Page Not Found"], "Social", 1, 1.0),
            OSINTSite("Facebook", "https://www.facebook.com/{username}", "status_code", 
                     ["200"], ["Page Not Found"], "Social", 1, 1.0),
            
            # Gaming Platforms
            OSINTSite("Steam", "https://steamcommunity.com/id/{username}", "status_code", 
                     ["200"], ["The specified profile could not be found"], "Gaming", 2, 1.0),
            OSINTSite("Twitch", "https://www.twitch.tv/{username}", "status_code", 
                     ["200"], ["Sorry, we couldn\\'t find that page"], "Gaming", 2, 1.0),
            OSINTSite("Roblox", "https://api.roblox.com/users/search?keyword={username}", "json_response", 
                     ["users"], [], "Gaming", 2, 0.8),
            
            # Adult Platforms (High Risk)
            OSINTSite("Pornhub", "https://www.pornhub.com/users/{username}", "status_code", 
                     ["200"], ["404 Not Found"], "Adult", 1, 2.0),
            OSINTSite("XVideos", "https://www.xvideos.com/pornstar/{username}", "status_code", 
                     ["200"], ["404"], "Adult", 1, 2.0),
            
            # Crypto & Finance
            OSINTSite("Coinbase", "https://www.coinbase.com/{username}", "status_code", 
                     ["200"], ["404"], "Crypto", 2, 1.0),
            OSINTSite("Binance", "https://www.binance.com/en/user/{username}", "status_code", 
                     ["200"], ["404"], "Crypto", 2, 1.0),
            
            # Dev Platforms
            OSINTSite("Stack Overflow", "https://stackoverflow.com/users/{username}", "status_code", 
                     ["200"], ["Page Not Found"], "Dev", 2, 1.0),
            OSINTSite("CodePen", "https://codepen.io/{username}", "status_code", 
                     ["200"], ["404"], "Dev", 2, 1.0),
            OSINTSite("Replit", "https://replit.com/@{username}", "status_code", 
                     ["200"], ["404"], "Dev", 2, 1.0),
            OSINTSite("GitLab", "https://gitlab.com/{username}", "status_code", 
                     ["200"], ["404"], "Dev", 2, 1.0),
            OSINTSite("Bitbucket", "https://bitbucket.org/{username}", "status_code", 
                     ["200"], ["Repository not found"], "Dev", 2, 1.0),
            
            # Music & Content
            OSINTSite("YouTube", "https://www.youtube.com/@{username}", "status_code", 
                     ["200"], ["This channel doesn't exist"], "Social", 2, 1.0),
            OSINTSite("TikTok", "https://www.tiktok.com/@{username}", "status_code", 
                     ["200"], ["Couldn't find this account"], "Social", 2, 1.0),
            OSINTSite("SoundCloud", "https://soundcloud.com/{username}", "status_code", 
                     ["200"], ["404 - Not Found"], "Social", 2, 1.0),
            OSINTSite("Medium", "https://medium.com/@{username}", "content_string", 
                     ["Stories by"], ["404"], "Social", 2, 1.0),
            OSINTSite("DeviantArt", "https://www.deviantart.com/{username}", "status_code", 
                     ["200"], ["The page you are looking for can't be found"], "Social", 2, 1.0),
            
            # Forums & Communities
            OSINTSite("Hacker News", "https://news.ycombinator.com/user?id={username}", "content_string", 
                     ["karma", "submissions"], ["No such user"], "Dev", 3, 1.0),
            OSINTSite("Quora", "https://www.quora.com/profile/{username}", "status_code", 
                     ["200"], ["404"], "Social", 3, 1.0),
            
            # Additional Social
            OSINTSite("Pinterest", "https://www.pinterest.com/{username}/", "status_code", 
                     ["200"], ["Oops, we couldn't find that page"], "Social", 3, 1.0),
            OSINTSite("Snapchat", "https://www.snapchat.com/add/{username}", "status_code", 
                     ["200"], ["Couldn't find that username"], "Social", 3, 2.0),
            OSINTSite("Discord", "https://discord.com/users/{username}", "status_code", 
                     ["200"], ["Unknown User"], "Social", 3, 1.0),
            
            # Professional & Business
            OSINTSite("Behance", "https://www.behance.net/{username}", "status_code", 
                     ["200"], ["Page Not Found"], "Social", 3, 1.0),
            OSINTSite("Dribbble", "https://dribbble.com/{username}", "status_code", 
                     ["200"], ["404"], "Social", 3, 1.0),
            
            # Dating & Lifestyle
            OSINTSite("Tinder", "https://www.gotinder.com/@{username}", "status_code", 
                     ["200"], ["404"], "Social", 3, 2.0),
            OSINTSite("OKCupid", "https://www.okcupid.com/profile/{username}", "status_code", 
                     ["200"], ["Page not found"], "Social", 3, 2.0),
        ]
        
        return sorted(sites, key=lambda x: (x.priority, x.rate_limit))
    
    def get_scan_summary(self, evidence_items: List[EvidenceItem]) -> Dict[str, Any]:
        """Generate summary of OSINT scan results."""
        summary = {
            "total_matches": len(evidence_items),
            "categories_found": {},
            "highest_risk_matches": [],
            "social_platforms": 0,
            "dev_platforms": 0,
            "gaming_platforms": 0,
            "adult_platforms": 0,
            "crypto_platforms": 0
        }
        
        for item in evidence_items:
            if item.type == "osint_match":
                category = item.metadata.get("category", "Unknown")
                confidence = item.metadata.get("confidence", 0)
                
                # Count by category
                summary["categories_found"][category] = summary["categories_found"].get(category, 0) + 1
                
                # Count specific platform types
                if category == "Social":
                    summary["social_platforms"] += 1
                elif category == "Dev":
                    summary["dev_platforms"] += 1
                elif category == "Gaming":
                    summary["gaming_platforms"] += 1
                elif category == "Adult":
                    summary["adult_platforms"] += 1
                elif category == "Crypto":
                    summary["crypto_platforms"] += 1
                
                # High risk matches (adult sites + high confidence social)
                if category == "Adult" or confidence > 0.8:
                    summary["highest_risk_matches"].append({
                        "platform": item.metadata.get("site_name"),
                        "url": item.metadata.get("site_url"),
                        "category": category,
                        "confidence": confidence
                    })
        
        return summary