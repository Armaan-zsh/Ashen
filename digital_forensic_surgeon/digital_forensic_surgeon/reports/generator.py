"""Advanced report generator for Digital Forensic Surgeon - Phase 4: The Dox Dossier."""

from __future__ import annotations

import os
import json
import platform
import getpass
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
import tempfile

try:
    from jinja2 import Template, Environment, FileSystemLoader
    JINJA2_AVAILABLE = True
except ImportError:
    JINJA2_AVAILABLE = False

from digital_forensic_surgeon.core.models import EvidenceItem, ForensicResult
from digital_forensic_surgeon.core.exceptions import ScannerError


class ReportGenerator:
    """Advanced report generator with interactive visualizations."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.template_path = Path(__file__).parent / "templates" / "report.html"
        
        # Initialize Jinja2 environment if available
        if JINJA2_AVAILABLE:
            template_dir = self.template_path.parent
            self.jinja_env = Environment(
                loader=FileSystemLoader(str(template_dir)),
                autoescape=True
            )
        else:
            self.jinja_env = None
    
    def generate_html_report(self, result: ForensicResult, output_path: Optional[str] = None) -> str:
        """Generate an interactive HTML report with maps and timelines."""
        
        if not output_path:
            output_dir = Path.cwd() / "forensic_reports"
            output_dir.mkdir(exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = str(output_dir / f"forensic_report_{timestamp}.html")
        
        # Prepare data for the template
        report_data = self._prepare_report_data(result)
        
        # Generate HTML
        if self.jinja_env:
            try:
                template = self.jinja_env.get_template("report.html")
                html_content = template.render(**report_data)
            except Exception as e:
                # Fallback to simple HTML generation
                html_content = self._generate_simple_html(report_data)
        else:
            html_content = self._generate_simple_html(report_data)
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_path
    
    def _prepare_report_data(self, result: ForensicResult) -> Dict[str, Any]:
        """Prepare all data for the HTML template."""
        
        # Basic scan information
        scan_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # System information
        system_info = {
            "username": getpass.getuser(),
            "hostname": platform.node(),
            "platform": platform.system(),
            "location": self._estimate_location(result)
        }
        
        # Extract GPS data from evidence items
        map_data = self.generate_map_data(result.evidence_items)
        
        # Extract timeline data
        timeline_data = self.generate_timeline_data(result.evidence_items)
        
        # Extract personal data
        personal_data = self._extract_personal_data(result.evidence_items)
        
        # Extract OSINT matches
        osint_matches = self._extract_osint_matches(result.evidence_items)
        
        # Extract browser data
        browser_data = self._extract_browser_data(result.evidence_items)
        
        # Calculate dox score
        dox_score = self._calculate_dox_score(result.evidence_items, personal_data, osint_matches, map_data)
        
        # Risk assessment
        overall_risk_level = self._assess_overall_risk(result.evidence_items, dox_score)
        
        # Generate attack scenarios
        attack_scenarios = self._generate_attack_scenarios(result.evidence_items, personal_data, osint_matches)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(result.evidence_items, personal_data, osint_matches, map_data)
        
        return {
            # Template variables
            "dox_score": dox_score,
            "scan_timestamp": scan_timestamp,
            "system_info": system_info,
            "total_evidence": len(result.evidence_items),
            "evidence_categories": list(set(item.type for item in result.evidence_items)),
            
            # Data for visualizations
            "map_data": map_data,
            "timeline_data": timeline_data,
            
            # Personal dossier data
            "personal_data": personal_data,
            "osint_matches": osint_matches,
            "gaming_matches": [m for m in osint_matches if m.get("category") == "Gaming"],
            "financial_evidence": self._extract_financial_evidence(result.evidence_items),
            
            # Browser intelligence
            "browser_profiles": browser_data.get("profiles", []),
            "autofill_data": browser_data.get("autofill", []),
            "download_data": browser_data.get("downloads", []),
            
            # Threat assessment
            "overall_risk_level": overall_risk_level,
            "attack_scenarios": attack_scenarios,
            "recommendations": recommendations
        }
    
    def generate_map_data(self, evidence_items: List[EvidenceItem]) -> List[Dict[str, Any]]:
        """Extract GPS data from evidence items for map visualization."""
        map_locations = []
        
        for item in evidence_items:
            if (item.type == "file" and 
                item.metadata and 
                item.metadata.get("has_gps") and
                item.metadata.get("gps_latitude") and
                item.metadata.get("gps_longitude")):
                
                location = {
                    "lat": float(item.metadata["gps_latitude"]),
                    "lon": float(item.metadata["gps_longitude"]),
                    "filename": os.path.basename(item.path),
                    "timestamp": item.metadata.get("datetimeoriginal", item.timestamp.strftime("%Y-%m-%d %H:%M:%S")),
                    "camera": f"{item.metadata.get('camera_make', '')} {item.metadata.get('camera_model', '')}".strip(),
                    "address": item.metadata.get("gps_coordinates", "")
                }
                map_locations.append(location)
        
        return map_locations
    
    def generate_timeline_data(self, evidence_items: List[EvidenceItem]) -> List[Dict[str, Any]]:
        """Generate timeline data from various evidence sources."""
        timeline_items = []
        
        for item in evidence_items:
            # Skip items without timestamps
            if not item.timestamp:
                continue
            
            timeline_item = {
                "id": item.id,
                "content": self._get_timeline_content(item),
                "start": item.timestamp.isoformat(),
                "type": self._get_timeline_type(item.type),
                "className": f"timeline-{item.type}"
            }
            timeline_items.append(timeline_item)
        
        # Sort by timestamp
        timeline_items.sort(key=lambda x: x["start"])
        
        return timeline_items
    
    def _get_timeline_content(self, item: EvidenceItem) -> str:
        """Get readable content for timeline item."""
        if item.type == "file":
            filename = os.path.basename(item.path)
            return f"📄 File: {filename}"
        elif item.type == "browser_download":
            return f"💾 Download: {os.path.basename(item.content)}"
        elif item.type == "browser_autofill":
            return f"📝 Form: {item.metadata.get('name', 'Unknown')}"
        elif item.type == "osint_match":
            platform = item.metadata.get("site_name", "Unknown")
            return f"🌐 OSINT: Found on {platform}"
        elif item.type == "wifi_connection":
            ssid = item.metadata.get("ssid", "Unknown")
            return f"📶 WiFi: Connected to {ssid}"
        else:
            return f"🔍 Evidence: {item.type}"
    
    def _get_timeline_type(self, item_type: str) -> str:
        """Get timeline item type for Vis.js."""
        type_mapping = {
            "file": "box",
            "browser_download": "box",
            "browser_autofill": "box",
            "osint_match": "point",
            "wifi_connection": "box",
            "network_scan": "box"
        }
        return type_mapping.get(item_type, "box")
    
    def _extract_personal_data(self, evidence_items: List[EvidenceItem]) -> Dict[str, str]:
        """Extract personal information from evidence items."""
        personal_data = {
            "full_name": None,
            "email": None,
            "phone": None,
            "address": None
        }
        
        for item in evidence_items:
            if item.type == "browser_autofill" and item.metadata.get("autofill_data"):
                for data in item.metadata["autofill_data"]:
                    field_name = data.get("name", "").lower()
                    field_value = data.get("value", "")
                    
                    # Email detection
                    if any(term in field_name for term in ["email", "e-mail"]) and "@" in field_value:
                        personal_data["email"] = field_value
                    # Phone detection
                    elif any(term in field_name for term in ["phone", "mobile", "tel"]) and len(field_value) >= 10:
                        personal_data["phone"] = field_value
                    # Name detection
                    elif any(term in field_name for term in ["name", "firstname", "lastname", "fullname"]):
                        if not personal_data["full_name"] or len(field_value) > len(personal_data["full_name"]):
                            personal_data["full_name"] = field_value
                    # Address detection
                    elif any(term in field_name for term in ["address", "street", "location"]):
                        if not personal_data["address"] or len(field_value) > len(personal_data["address"]):
                            personal_data["address"] = field_value
        
        return personal_data
    
    def _extract_osint_matches(self, evidence_items: List[EvidenceItem]) -> List[Dict[str, Any]]:
        """Extract OSINT match information."""
        osint_matches = []
        
        for item in evidence_items:
            if item.type == "osint_match":
                match = {
                    "platform": item.metadata.get("site_name", "Unknown"),
                    "username": item.metadata.get("username", "Unknown"),
                    "url": item.metadata.get("site_url", ""),
                    "category": item.metadata.get("category", "Unknown"),
                    "risk_level": self._assess_osint_risk(item.metadata.get("category", ""), item.metadata.get("confidence", 0))
                }
                osint_matches.append(match)
        
        return osint_matches
    
    def _assess_osint_risk(self, category: str, confidence: float) -> str:
        """Assess risk level of OSINT match."""
        if category == "Adult" or confidence > 0.9:
            return "Critical"
        elif category in ["Social", "Crypto"] or confidence > 0.8:
            return "High"
        elif category == "Dev" or confidence > 0.6:
            return "Medium"
        else:
            return "Low"
    
    def _extract_browser_data(self, evidence_items: List[EvidenceItem]) -> Dict[str, Any]:
        """Extract browser-related data."""
        browser_data = {
            "profiles": [],
            "autofill": [],
            "downloads": []
        }
        
        for item in evidence_items:
            if item.type == "browser_profile":
                browser_data["profiles"].append({
                    "browser": item.metadata.get("browser", "Unknown"),
                    "path": item.metadata.get("profile_path", ""),
                    "scanned_at": item.metadata.get("scanned_at", "")
                })
            
            elif item.type == "browser_autofill" and item.metadata.get("autofill_data"):
                for data in item.metadata["autofill_data"]:
                    browser_data["autofill"].append({
                        "field_name": data.get("name", ""),
                        "field_value": data.get("value", ""),
                        "count": data.get("count", 1),
                        "timestamp": item.timestamp.strftime("%Y-%m-%d %H:%M:%S")
                    })
            
            elif item.type == "browser_download" and item.metadata.get("download_data"):
                for data in item.metadata["download_data"]:
                    browser_data["downloads"].append({
                        "filename": os.path.basename(data.get("target_path", "")),
                        "source_url": data.get("url", ""),
                        "timestamp": data.get("start_time", item.timestamp).strftime("%Y-%m-%d %H:%M:%S") if data.get("start_time") else item.timestamp.strftime("%Y-%m-%d %H:%M:%S")
                    })
        
        return browser_data
    
    def _extract_financial_evidence(self, evidence_items: List[EvidenceItem]) -> List[Dict[str, Any]]:
        """Extract financial-related evidence."""
        financial_evidence = []
        
        financial_keywords = [
            "credit", "card", "bank", "account", "balance", "payment",
            "transaction", "salary", "income", "tax", "ssn", "routing"
        ]
        
        for item in evidence_items:
            content_lower = item.content.lower()
            metadata_lower = str(item.metadata).lower()
            
            if any(keyword in content_lower or keyword in metadata_lower for keyword in financial_keywords):
                financial_evidence.append({
                    "type": item.type,
                    "description": item.content[:100] + "..." if len(item.content) > 100 else item.content,
                    "location": item.path,
                    "timestamp": item.timestamp.strftime("%Y-%m-%d %H:%M:%S")
                })
        
        return financial_evidence[:10]  # Limit to top 10
    
    def _calculate_dox_score(self, evidence_items: List[EvidenceItem], personal_data: Dict[str, str], osint_matches: List[Dict[str, Any]], map_data: List[Dict[str, Any]]) -> int:
        """Calculate the doxability score (0-100)."""
        score = 0
        
        # Personal data found (40 points max)
        if personal_data.get("full_name"):
            score += 10
        if personal_data.get("email"):
            score += 15
        if personal_data.get("phone"):
            score += 10
        if personal_data.get("address"):
            score += 15
        
        # OSINT matches (30 points max)
        if osint_matches:
            high_risk_matches = [m for m in osint_matches if m.get("risk_level") in ["Critical", "High"]]
            social_matches = [m for m in osint_matches if m.get("category") == "Social"]
            score += min(len(high_risk_matches) * 10, 20)  # Max 20 for high-risk
            score += min(len(social_matches) * 2, 10)  # Max 10 for social
        
        # Geographic data (20 points max)
        score += min(len(map_data) * 5, 20)  # Each GPS location worth 5 points
        
        # Browser data (10 points max)
        autofill_count = sum(1 for item in evidence_items if item.type == "browser_autofill")
        download_count = sum(1 for item in evidence_items if item.type == "browser_download")
        score += min(autofill_count, 5)  # Max 5 for autofill items
        score += min(download_count, 5)  # Max 5 for downloads
        
        return min(score, 100)
    
    def _assess_overall_risk(self, evidence_items: List[EvidenceItem], dox_score: int) -> str:
        """Assess overall risk level based on evidence."""
        if dox_score >= 80:
            return "Critical"
        elif dox_score >= 60:
            return "High"
        elif dox_score >= 40:
            return "Medium"
        else:
            return "Low"
    
    def _estimate_location(self, result: ForensicResult) -> Optional[str]:
        """Estimate user location from evidence."""
        # Look for location in WiFi data or IP information
        for item in result.evidence_items:
            if item.type == "wifi_connection":
                ssid = item.metadata.get("ssid", "")
                # You could implement SSID-based location lookup here
                return f"Near WiFi: {ssid}"
        return None
    
    def _generate_attack_scenarios(self, evidence_items: List[EvidenceItem], personal_data: Dict[str, str], osint_matches: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Generate realistic attack scenarios."""
        scenarios = []
        
        # Scenario 1: Identity theft
        if personal_data.get("email") and personal_data.get("full_name"):
            scenarios.append({
                "title": "Identity Theft via Email",
                "description": f"Using your name '{personal_data['full_name']}' and email '{personal_data['email']}', an attacker could attempt password resets on your accounts.",
                "severity": "High"
            })
        
        # Scenario 2: Location tracking
        gps_items = [item for item in evidence_items if item.type == "file" and item.metadata.get("has_gps")]
        if gps_items:
            scenarios.append({
                "title": "Physical Location Tracking",
                "description": f"Found GPS coordinates in {len(gps_items)} photos. An attacker could track your movements and identify your home, work, and frequent locations.",
                "severity": "High"
            })
        
        # Scenario 3: Social engineering
        if osint_matches:
            scenarios.append({
                "title": "Social Engineering Attack",
                "description": f"Found your profiles on {len(osint_matches)} platforms. An attacker could gather personal details to impersonate you or gain trust.",
                "severity": "Medium"
            })
        
        # Scenario 4: Password attacks
        if personal_data.get("phone"):
            scenarios.append({
                "title": "SMS-Based Password Reset",
                "description": f"Your phone number '{personal_data['phone']}' could be used to reset passwords via SMS if not properly secured.",
                "severity": "Medium"
            })
        
        return scenarios
    
    def _generate_recommendations(self, evidence_items: List[EvidenceItem], personal_data: Dict[str, str], osint_matches: List[Dict[str, Any]], map_data: List[Dict[str, Any]]) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        # Critical recommendations based on findings
        if personal_data.get("email"):
            recommendations.append("Enable two-factor authentication on all accounts using your email")
        
        if personal_data.get("phone"):
            recommendations.append("Secure your phone number with carrier PIN and enable SIM lock")
        
        if map_data:
            recommendations.append("Remove GPS data from photos before sharing online - use tools like ExifCleaner")
        
        if osint_matches:
            recommendations.append("Review and tighten privacy settings on all social media platforms")
        
        if len([item for item in evidence_items if item.type == "browser_autofill"]) > 10:
            recommendations.append("Clear browser autofill data regularly and use a password manager")
        
        # General recommendations
        recommendations.extend([
            "Use unique, strong passwords for every account",
            "Regularly check for data breaches using services like HaveIBeenPwned",
            "Consider using a VPN to mask your IP address and location",
            "Enable automatic security updates on all devices",
            "Be cautious about what personal information you share online"
        ])
        
        return recommendations[:8]  # Limit to top 8 recommendations
    
    def _generate_simple_html(self, data: Dict[str, Any]) -> str:
        """Generate simple HTML if Jinja2 is not available."""
        # This is a fallback HTML generator
        return f"""
        <!DOCTYPE html>
        <html>
        <head><title>Digital Forensic Report</title></head>
        <body>
            <h1>Digital Forensic Surgery Report</h1>
            <p><strong>DOX SCORE:</strong> {data.get('dox_score', 0)}/100</p>
            <p><strong>Generated:</strong> {data.get('scan_timestamp', '')}</p>
            <p><strong>Evidence Items:</strong> {data.get('total_evidence', 0)}</p>
            <p><strong>Overall Risk:</strong> {data.get('overall_risk_level', 'Unknown')}</p>
            <p><em>Install Jinja2 for full interactive report: pip install jinja2</em></p>
        </body>
        </html>
        """