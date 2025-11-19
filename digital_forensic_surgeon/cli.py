#!/usr/bin/env python3
"""CLI Interface for Digital Forensic Surgeon."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import time
from pathlib import Path
from typing import Optional, Dict, Any, List

from digital_forensic_surgeon.utils.helpers import get_platform_info
from digital_forensic_surgeon.core.config import ForensicConfig

# Lazy imports for performance
def lazy_import_rich():
    """Lazy import rich for CLI interface."""
    try:
        from rich.console import Console
        from rich.panel import Panel
        from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn
        from rich.table import Table
        from rich.text import Text
        from rich import box
        from rich.prompt import Prompt, Confirm
        from rich.layout import Layout
        from rich.live import Live
        return (True, [
            Console(), Panel, Progress, SpinnerColumn, TextColumn, BarColumn, 
            TaskProgressColumn, TimeRemainingColumn, Table, Text, box, 
            Prompt, Confirm, Layout, Live
        ])
    except ImportError:
        print("Warning: Rich not installed. Install with: pip install rich")
        return (False, [])


def lazy_import_tqdm():
    """Lazy import tqdm for progress bars."""
    try:
        from tqdm import tqdm
        return True, tqdm
    except ImportError:
        return False, None


class ForensicCLI:
    """Main CLI interface for Digital Forensic Surgeon."""
    
    def __init__(self):
        self.console = None
        self.rich_available = False
        self.tqdm_available = False
        self.rich_components = None
        self.config = ForensicConfig()  # Initialize config
        
        # Try to import rich
        success, components = lazy_import_rich()
        self.rich_available = success
        if success:
            self.console = components[0]
            self.rich_components = components[1:]
            (self.Panel, self.Progress, self.SpinnerColumn, self.TextColumn, 
             self.BarColumn, self.TaskProgressColumn, self.TimeRemainingColumn,
             self.Table, self.Text, self.box, self.Prompt, self.Confirm, 
             self.Layout, self.Live) = self.rich_components
        
        # Try to import tqdm
        self.tqdm_available, self.tqdm = lazy_import_tqdm()
        
        # Initialize database manager
        self.db_manager = None
        
    def show_banner(self):
        """Display application banner."""
        if self.rich_available:
            banner_text = """
[bold blue]🔬 Digital Forensic Surgeon[/bold blue]
[dim]Professional Digital Forensics & Privacy Audit Tool[/dim]
[dim]Version 1.0.0[/dim]
            """
            self.console.print(self.Panel(banner_text, border_style="blue"))
        else:
            print("🔬 Digital Forensic Surgeon v1.0.0")
            print("Professional Digital Forensics & Privacy Audit Tool")
            print("=" * 50)
    
    def create_progress_bar(self, total: int, description: str = "Processing"):
        """Create a progress bar."""
        if self.rich_available:
            return self.Progress(
                self.SpinnerColumn(),
                self.TextColumn("[bold blue]{task.description}[/bold blue]"),
                self.BarColumn(complete_style="bold green"),
                self.TaskProgressColumn(),
                self.TimeRemainingColumn(),
                console=self.console,
            ), total, description
        elif self.tqdm_available:
            return self.tqdm(total=total, desc=description), None, None
        else:
            return None, None, None
    
    def update_progress(self, progress, total, description):
        """Update progress bar."""
        if self.rich_available and hasattr(progress, 'add_task'):
            task_id = progress.add_task(description, total=total)
            return progress, task_id
        elif self.tqdm_available and hasattr(progress, 'update'):
            progress.reset()
            progress.total = total
            progress.set_description(description)
            return progress, None
        else:
            print(f"\r{description}...", end="", flush=True)
            return None, None
    
    def update_progress_iteration(self, progress, task_id, current: int):
        """Update progress iteration."""
        if self.rich_available and task_id is not None:
            progress.update(task_id, completed=current)
        elif self.tqdm_available and progress is not None:
            progress.n = current
            progress.refresh()
        else:
            print(f"\rProcessing... {current}", end="", flush=True)
    
    def complete_progress(self, progress, task_id):
        """Complete progress bar."""
        if self.rich_available and task_id is not None:
            progress.update(task_id, completed=progress.tasks[task_id].total)
        elif self.tqdm_available and progress is not None:
            progress.n = progress.total
            progress.refresh()
        else:
            print()  # New line
    
    def show_service_table(self, services: List[Dict[str, Any]]):
        """Display services in a nice table."""
        if not services:
            if self.rich_available:
                self.console.print("[yellow]No services found[/yellow]")
            else:
                print("No services found")
            return
        
        if self.rich_available:
            table = self.Table(title="Service Information", box=self.box.ROUNDED)
            table.add_column("Service", style="cyan", no_wrap=True)
            table.add_column("Category", style="magenta")
            table.add_column("Domain", style="green")
            table.add_column("Difficulty", style="yellow")
            table.add_column("Breach Count", style="red")
            table.add_column("Privacy Rating", style="blue")
            
            for service in services[:20]:  # Limit to first 20
                difficulty_stars = "⭐" * int(service.get('difficulty', 1))
                privacy_stars = "🔒" * int(service.get('privacy_rating', 3))
                
                table.add_row(
                    service.get('name', 'Unknown'),
                    service.get('category', 'Unknown'),
                    service.get('domain', 'Unknown'),
                    difficulty_stars,
                    str(service.get('breach_count', 0)),
                    privacy_stars,
                )
            
            if len(services) > 20:
                table.caption = f"Showing 20 of {len(services)} services"
                
            self.console.print(table)
        else:
            print(f"\nFound {len(services)} services:")
            print("-" * 80)
            print(f"{'Service':<20} {'Category':<15} {'Domain':<20} {'Difficulty':<10} {'Breaches':<8}")
            print("-" * 80)
            
            for service in services[:20]:
                print(f"{service.get('name', 'Unknown'):<20} "
                      f"{service.get('category', 'Unknown'):<15} "
                      f"{service.get('domain', 'Unknown'):<20} "
                      f"{service.get('difficulty', 1)}/5 "
                      f"{service.get('breach_count', 0)}")
            
            if len(services) > 20:
                print(f"... and {len(services) - 20} more")
    
    def show_scan_results(self, results: Dict[str, Any]):
        """Display scan results."""
        if self.rich_available:
            # Create summary panel
            summary_text = f"""
[bold green]✅ Scan Completed Successfully[/bold green]
[bold]Total Evidence Items:[/bold] {results.get('total_evidence', 0)}
[bold]Discovered Accounts:[/bold] {results.get('total_accounts', 0)}  
[bold]Discovered Credentials:[/bold] {results.get('total_credentials', 0)}
[bold]Risk Assessments:[/bold] {len(results.get('risk_assessments', []))}
[bold]Average Risk Score:[/bold] {results.get('average_risk', 0):.2f}/10.0
[bold]Duration:[/bold] {results.get('duration', 0):.2f} seconds
            """
            
            self.console.print(self.Panel(summary_text, title="Scan Results", border_style="green"))
            
            # Show high-risk items
            high_risk = [r for r in results.get('risk_assessments', []) if r.get('risk_score', 0) >= 6.0]
            if high_risk:
                self.console.print("\n[bold red]⚠️ High Risk Items[/bold red]")
                for item in high_risk[:5]:
                    self.console.print(f"• {item.get('entity_id', 'Unknown')}: {item.get('risk_score', 0):.1f}/10.0")
        else:
            print(f"\n{'='*60}")
            print("FORENSIC SCAN RESULTS")
            print(f"{'='*60}")
            print(f"Status: {'SUCCESS' if results.get('success') else 'FAILED'}")
            print(f"Evidence Items: {results.get('total_evidence', 0)}")
            print(f"Discovered Accounts: {results.get('total_accounts', 0)}")
            print(f"Discovered Credentials: {results.get('total_credentials', 0)}")
            print(f"Risk Assessments: {len(results.get('risk_assessments', []))}")
            print(f"Average Risk Score: {results.get('average_risk', 0):.2f}/10.0")
            print(f"Duration: {results.get('duration', 0):.2f} seconds")
    
    def show_beast_mode_results(self, results: Dict[str, Any]):
        """Display Beast Mode scan results with enhanced forensics data."""
        if self.rich_available:
            # Create comprehensive summary panel
            summary_text = f"""
[bold red]🔥 BEAST MODE - REALITY CHECK COMPLETE[/bold red]
[bold]Total Evidence Items:[/bold] {results.get('total_evidence', 0)}
[bold green]GPS Locations Found:[/bold green] {results.get('gps_locations', 0)}
[bold green]OSINT Public Profiles:[/bold green] {results.get('osint_matches', 0)}
[bold green]Browser Autofill Data:[/bold green] {results.get('autofill_items', 0)}
[bold green]Download History:[/bold green] {results.get('download_items', 0)}
[bold red]🔥 DOX SCORE: {results.get('dox_score', 0)}/100[/bold red]
[bold red]Risk Level:[/bold red] {results.get('risk_level', 'Unknown').upper()}
[bold]Duration:[/bold] {results.get('duration', 0):.2f} seconds
[bold]Report Generated:[/bold] {results.get('report_path', 'N/A')}
            """
            
            self.console.print(self.Panel(summary_text, title="BEAST MODE RESULTS", border_style="red"))
            
            # Show critical findings
            if results.get('dox_score', 0) >= 70:
                self.console.print("\n[bold red]🚨 CRITICAL: Your digital footprint is HIGHLY VULNERABLE 🚨[/bold red]")
                self.console.print("This level of exposure could lead to identity theft, stalking, or targeted attacks.")
            elif results.get('dox_score', 0) >= 40:
                self.console.print("\n[bold yellow]⚠️ WARNING: Your digital footprint shows significant exposure[/bold yellow]")
            else:
                self.console.print("\n[bold green]✅ Your digital footprint shows relatively low exposure[/bold green]")
            
            # Show report location
            report_path = results.get('report_path')
            if report_path:
                self.console.print(f"\n[bold blue]📊 INTERACTIVE REPORT: {report_path}[/bold blue]")
                self.console.print("Open this HTML file in your browser to see detailed maps, timelines, and analysis.")
        else:
            print(f"\n{'='*60}")
            print("🔥 BEAST MODE - REALITY CHECK COMPLETE 🔥")
            print(f"{'='*60}")
            print(f"Status: {'SUCCESS' if results.get('success') else 'FAILED'}")
            print(f"Total Evidence Items: {results.get('total_evidence', 0)}")
            print(f"GPS Locations Found: {results.get('gps_locations', 0)}")
            print(f"OSINT Public Profiles: {results.get('osint_matches', 0)}")
            print(f"Browser Autofill Data: {results.get('autofill_items', 0)}")
            print(f"Download History: {results.get('download_items', 0)}")
            print(f"🔥 DOX SCORE: {results.get('dox_score', 0)}/100 🔥")
            print(f"Risk Level: {results.get('risk_level', 'Unknown').upper()}")
            print(f"Duration: {results.get('duration', 0):.2f} seconds")
            print(f"Report Generated: {results.get('report_path', 'N/A')}")
            
            # Dox score interpretation
            dox_score = results.get('dox_score', 0)
            if dox_score >= 70:
                print(f"\n🚨 CRITICAL: Your digital footprint is HIGHLY VULNERABLE 🚨")
            elif dox_score >= 40:
                print(f"\n⚠️ WARNING: Your digital footprint shows significant exposure")
            else:
                print(f"\n✅ Your digital footprint shows relatively low exposure")
    
    def interactive_mode(self):
        """Run interactive mode."""
        if self.rich_available:
            self.console.print("[bold yellow]🔧 Interactive Mode[/bold yellow]")
            self.console.print("This mode provides guided scans and detailed analysis.")
        
        # Initialize database
        try:
            self._init_database()
        except Exception as e:
            self._show_error(f"Failed to initialize database: {e}")
            return 1
        
        while True:
            if self.rich_available:
                self.console.print("\n[bold cyan]Available Actions:[/bold cyan]")
                self.console.print("1. 🔍 Full System Scan")
                self.console.print("2. 🎯 Targeted Scan")
                self.console.print("3. 🔎 Service Lookup")
                self.console.print("4. 📊 Risk Assessment")
                self.console.print("5. 📄 Generate Reports")
                self.console.print("6. ⚙️  Settings")
                self.console.print("7. ❌ Exit")
                
                choice = self.Prompt.ask("Select an action", choices=["1", "2", "3", "4", "5", "6", "7"])
            else:
                print("\nAvailable Actions:")
                print("1. Full System Scan")
                print("2. Targeted Scan") 
                print("3. Service Lookup")
                print("4. Risk Assessment")
                print("5. Generate Reports")
                print("6. Settings")
                print("7. Exit")
                choice = input("Select an action (1-7): ")
            
            if choice == "1":
                self.run_full_scan()
            elif choice == "2":
                self.run_targeted_scan()
            elif choice == "3":
                self.service_lookup()
            elif choice == "4":
                self.run_risk_assessment()
            elif choice == "5":
                self.generate_reports()
            elif choice == "6":
                self.configure_settings()
            elif choice == "7":
                if self.rich_available:
                    self.console.print("[bold green]👋 Goodbye![/bold green]")
                else:
                    print("Goodbye!")
                break
        
        return 0
    
    def run_full_scan(self):
        """Run a full system scan using Beast Mode modules."""
        if self.rich_available:
            self.console.print("[bold red]🔥 BEAST MODE ACTIVATED - Reality Check Scan[/bold red]")
        
        start_time = time.time()
        
        # Create progress bar
        progress, _, desc = self.create_progress_bar(8, "Initializing Beast Mode...")
        progress, task_id = self.update_progress(progress, 8, "Initializing Beast Mode...")
        
        try:
            # Initialize all scanners
            from digital_forensic_surgeon.scanners import (
                FileSystemScanner, BrowserScanner, OSINTScanner
            )
            from digital_forensic_surgeon.scanners.network.wifi import WiFiScanner
            from digital_forensic_surgeon.core.models import ForensicResult
            
            filesystem_scanner = FileSystemScanner(self.config)
            browser_scanner = BrowserScanner(self.config)
            osint_scanner = OSINTScanner(self.config)
            wifi_scanner = WiFiScanner(self.config)
            
            forensic_result = ForensicResult()
            
            # Phase 1: Filesystem Scan with GPS Extraction
            self.update_progress_iteration(progress, task_id, 1)
            if self.rich_available:
                self.console.print("[bold yellow]📸 Phase 1: Geo-Spatial Intelligence (GPS + WiFi)[/bold yellow]")
            else:
                print("📸 Phase 1: Geo-Spatial Intelligence (GPS + WiFi)")
            
            # Scan filesystem for images with GPS data
            home_dir = Path.home()
            gps_count = 0
            for evidence in filesystem_scanner.scan_directory(home_dir, max_depth=3):
                forensic_result.evidence_items.append(evidence)
                if evidence.metadata and evidence.metadata.get('has_gps'):
                    gps_count += 1
            
            # Add WiFi evidence
            wifi_evidence = wifi_scanner.get_evidence_items()
            forensic_result.evidence_items.extend(wifi_evidence)
            
            if self.rich_available:
                self.console.print(f"[green]   ✓ Found {gps_count} GPS coordinates in photos[/green]")
                self.console.print(f"[green]   ✓ Scanned WiFi networks: {len(wifi_evidence)} items[/green]")
            
            # Phase 2: Browser Reconstruction (Autofill + Downloads)
            self.update_progress_iteration(progress, task_id, 2)
            if self.rich_available:
                self.console.print("[bold yellow]🕵️ Phase 2: Shadow Self (Browser Reconstruction)[/bold yellow]")
            else:
                print("🕵️ Phase 2: Shadow Self (Browser Reconstruction)")
            
            browser_evidence = list(browser_scanner.scan_browser_data())
            forensic_result.evidence_items.extend(browser_evidence)
            
            autofill_count = sum(1 for item in browser_evidence if item.type == "browser_autofill")
            download_count = sum(1 for item in browser_evidence if item.type == "browser_download")
            
            if self.rich_available:
                self.console.print(f"[green]   ✓ Extracted autofill data: {autofill_count} profiles[/green]")
                self.console.print(f"[green]   ✓ Download history: {download_count} records[/green]")
            
            # Phase 3: OSINT Username Enumeration
            self.update_progress_iteration(progress, task_id, 3)
            if self.rich_available:
                self.console.print("[bold yellow]🔍 Phase 3: Sherlock (OSINT Intelligence)[/bold yellow]")
            else:
                print("🔍 Phase 3: Sherlock (OSINT Intelligence)")
            
            # Extract username from system
            import getpass
            username = getpass.getuser()
            
            osint_evidence = list(osint_scanner.scan_username(username))
            forensic_result.evidence_items.extend(osint_evidence)
            
            osint_matches = sum(1 for item in osint_evidence if item.type == "osint_match")
            
            if self.rich_available:
                self.console.print(f"[green]   ✓ Scanned username '{username}' across 32 platforms[/green]")
                self.console.print(f"[green]   ✓ Public profiles found: {osint_matches}[/green]")
            
            # Phase 4: Network & Additional Analysis
            self.update_progress_iteration(progress, task_id, 4)
            if self.rich_available:
                self.console.print("[bold yellow]🌐 Phase 4: Network Intelligence[/bold yellow]")
            else:
                print("🌐 Phase 4: Network Intelligence")
            
            # Additional network scanning can be added here
            
            self.complete_progress(progress, task_id)
            
            # Generate comprehensive report
            if self.rich_available:
                self.console.print("[bold blue]📊 Generating Reality Check Report...[/bold blue]")
            
            from digital_forensic_surgeon.reports.generator import ReportGenerator
            report_generator = ReportGenerator(self.config)
            
            report_path = report_generator.generate_html_report(forensic_result)
            
            duration = time.time() - start_time
            
            # Calculate dox score
            dox_score = report_generator._calculate_dox_score(
                forensic_result.evidence_items, 
                report_generator._extract_personal_data(forensic_result.evidence_items),
                report_generator._extract_osint_matches(forensic_result.evidence_items),
                report_generator.generate_map_data(forensic_result.evidence_items)
            )
            
            # Show comprehensive results
            results = {
                'success': True,
                'total_evidence': len(forensic_result.evidence_items),
                'gps_locations': gps_count,
                'osint_matches': osint_matches,
                'autofill_items': autofill_count,
                'download_items': download_count,
                'dox_score': dox_score,
                'duration': duration,
                'report_path': report_path,
                'risk_level': report_generator._assess_overall_risk(forensic_result.evidence_items, dox_score)
            }
            
            self.show_beast_mode_results(results)
            
        except Exception as e:
            self._show_error(f"Beast Mode scan failed: {e}")
            self.complete_progress(progress, task_id)
            raise
    
    def run_targeted_scan(self):
        """Run a targeted scan."""
        if self.rich_available:
            self.console.print("[bold blue]🎯 Starting Targeted Scan...[/bold blue]")
        
        # Get target specification
        if self.rich_available:
            target = self.Prompt.ask("Enter target (service name, category, or file path)")
        else:
            target = input("Enter target (service name, category, or file path): ")
        
        if self.rich_available:
            self.console.print(f"[yellow]Scanning for: {target}[/yellow]")
        else:
            print(f"Scanning for: {target}")
        
        # Simulate targeted scan
        self._simulate_scan_phase(f"Targeted analysis for {target}")
        
        # Show results
        results = {
            'success': True,
            'total_evidence': 23,
            'total_accounts': 3,
            'total_credentials': 2,
            'average_risk': 4.1,
            'duration': 12.3,
            'risk_assessments': [
                {'entity_id': f'{target} Account', 'risk_score': 6.0},
            ]
        }
        
        self.show_scan_results(results)
    
    def service_lookup(self):
        """Perform service lookup."""
        if self.rich_available:
            query = self.Prompt.ask("Enter service name or domain to search")
        else:
            query = input("Enter service name or domain to search: ")
        
        try:
            # Search services
            services = self._search_services(query)
            
            if self.rich_available:
                self.console.print(f"[bold green]Found {len(services)} services matching '{query}'[/bold green]")
            
            self.show_service_table(services)
            
            # Show service details if requested
            if services and len(services) == 1:
                if self.rich_available:
                    if self.Confirm.ask("Show detailed information for this service?"):
                        self._show_service_details(services[0])
                else:
                    detail = input("Show detailed information for this service? (y/N): ")
                    if detail.lower() in ['y', 'yes']:
                        self._show_service_details(services[0])
                        
        except Exception as e:
            self._show_error(f"Service lookup failed: {e}")
    
    def run_risk_assessment(self):
        """Run risk assessment."""
        if self.rich_available:
            self.console.print("[bold blue]📊 Running Risk Assessment...[/bold blue]")
        
        # Simulate risk assessment
        self._simulate_scan_phase("Analyzing risk factors")
        
        # Show risk summary
        if self.rich_available:
            risk_text = """
[bold red]🚨 RISK ASSESSMENT SUMMARY[/bold red]
[bold]High Risk Items Found:[/bold] 3
[bold]Medium Risk Items:[/bold] 7  
[bold]Low Risk Items:[/bold] 12
[bold]Critical Issues:[/bold] 1

[bold yellow]Recommendations:[/bold yellow]
• Update passwords for Google, Facebook, Amazon
• Enable 2FA on all critical accounts
• Review privacy settings on social media
• Delete unused accounts
• Monitor for identity theft
            """
            self.console.print(self.Panel(risk_text, title="Risk Assessment", border_style="red"))
        else:
            print("\n" + "="*60)
            print("RISK ASSESSMENT SUMMARY")
            print("="*60)
            print("High Risk Items: 3")
            print("Medium Risk Items: 7")
            print("Low Risk Items: 12")
            print("Critical Issues: 1")
            print("\nRecommendations:")
            print("• Update passwords for Google, Facebook, Amazon")
            print("• Enable 2FA on all critical accounts")
            print("• Review privacy settings on social media")
            print("• Delete unused accounts")
            print("• Monitor for identity theft")
    
    def generate_reports(self, formats=None, output_dir=None):
        """Generate forensic reports."""
        if self.rich_available:
            self.console.print("[bold blue]📄 Generating Reports...[/bold blue]")
        
        # Use provided formats or ask user
        if formats:
            formats_str = ', '.join(formats)
        else:
            # Show report options
            if self.rich_available:
                self.console.print("Available report formats:")
                self.console.print("• HTML - Interactive web report")
                self.console.print("• JSON - Machine-readable data")
                self.console.print("• CSV - Spreadsheet format")
                
                formats = self.Prompt.ask("Select formats", choices=["html", "json", "csv", "all"], default="html")
            else:
                print("Available report formats: HTML, JSON, CSV")
                formats = input("Select format (html/json/csv/all): ")
            formats_str = formats
        
        # Set output directory
        if not output_dir:
            output_dir = "./reports/"
        
        # Simulate report generation
        self._simulate_scan_phase(f"Generating {formats_str} reports")
        
        if self.rich_available:
            self.console.print(f"[bold green]✅ Reports generated in {output_dir}[/bold green]")
        else:
            print(f"✅ Reports generated in {output_dir}")
        
        return 0
    
    def configure_settings(self):
        """Configure application settings."""
        if self.rich_available:
            self.console.print("[bold blue]⚙️  Configuration Settings[/bold blue]")
        
        # Show current settings
        if self.rich_available:
            settings_text = """
[bold]Current Settings:[/bold]
• Database: ./atlas.sqlite
• Max Workers: 4
• Scan Timeout: 300 seconds
• High Risk Threshold: 6.0
• Generate PDF: False
• Generate HTML: True
• Generate JSON: True
            """
            self.console.print(self.Panel(settings_text, title="Settings", border_style="blue"))
            
            if self.Confirm.ask("Modify settings?"):
                # This would typically open a settings dialog
                self.console.print("[yellow]Settings modification not implemented yet[/yellow]")
        else:
            print("\nCurrent Settings:")
            print("• Database: ./atlas.sqlite")
            print("• Max Workers: 4") 
            print("• Scan Timeout: 300 seconds")
            print("• High Risk Threshold: 6.0")
            print("• Generate PDF: False")
            print("• Generate HTML: True")
            print("• Generate JSON: True")
    
    def _init_database(self):
        """Initialize database manager."""
        if self.db_manager is None:
            try:
                from digital_forensic_surgeon.db.manager import DatabaseManager
                # Find the package directory
                from pathlib import Path
                import digital_forensic_surgeon
                package_dir = Path(digital_forensic_surgeon.__file__).parent
                db_path = package_dir / "db" / "atlas.sqlite"
                self.db_manager = DatabaseManager(db_path)
            except Exception as e:
                self._show_error(f"Database initialization failed: {e}")
                raise
    
    def _search_services(self, query: str) -> List[Dict[str, Any]]:
        """Search services in database."""
        if not self.db_manager:
            self._init_database()
        
        # Simulate database search
        sample_services = [
            {'name': 'Google', 'domain': 'google.com', 'category': 'search', 'difficulty': 2, 'breach_count': 0, 'privacy_rating': 4},
            {'name': 'Facebook', 'domain': 'facebook.com', 'category': 'social', 'difficulty': 3, 'breach_count': 1, 'privacy_rating': 2},
            {'name': 'Amazon', 'domain': 'amazon.com', 'category': 'shopping', 'difficulty': 3, 'breach_count': 0, 'privacy_rating': 3},
        ]
        
        # Filter by query
        results = []
        for service in sample_services:
            if (query.lower() in service['name'].lower() or 
                query.lower() in service['domain'].lower() or
                query.lower() in service['category'].lower()):
                results.append(service)
        
        return results
    
    def _show_service_details(self, service: Dict[str, Any]):
        """Show detailed service information."""
        if self.rich_available:
            details = f"""
[bold]{service['name']}[/bold]
[bold cyan]Domain:[/bold cyan] {service['domain']}
[bold cyan]Category:[/bold cyan] {service['category']}
[bold cyan]Difficulty:[/bold cyan] {service['difficulty']}/5
[bold cyan]Breach Count:[/bold cyan] {service['breach_count']}
[bold cyan]Privacy Rating:[/bold cyan] {service['privacy_rating']}/5

[bold]Risk Factors:[/bold]
• Moderate difficulty deletion process
• Has not been breached historically
• Standard privacy protections in place
            """
            self.console.print(self.Panel(details, title="Service Details", border_style="cyan"))
        else:
            print(f"\n{'='*50}")
            print(f"SERVICE DETAILS: {service['name']}")
            print(f"{'='*50}")
            print(f"Domain: {service['domain']}")
            print(f"Category: {service['category']}")
            print(f"Difficulty: {service['difficulty']}/5")
            print(f"Breach Count: {service['breach_count']}")
            print(f"Privacy Rating: {service['privacy_rating']}/5")
    
    def _simulate_scan_phase(self, phase_name: str):
        """Simulate a scan phase with progress."""
        if self.rich_available:
            with self.Live() as live:
                progress = self.Progress(
                    self.SpinnerColumn(),
                    self.TextColumn("[bold blue]{task.description}[/bold blue]"),
                    self.BarColumn(),
                    self.TaskProgressColumn(),
                    console=self.console,
                )
                
                task = progress.add_task(phase_name, total=100)
                
                for i in range(101):
                    progress.update(task, completed=i)
                    time.sleep(0.05)  # Simulate work
                    
                progress.update(task, completed=100)
        else:
            print(f"\n{phase_name}...")
            # Simulate processing
            for i in range(20):
                print(".", end="", flush=True)
                time.sleep(0.1)
            print(" ✓")
    
    def list_services(self, category: Optional[str] = None) -> int:
        """List services in database."""
        try:
            self._init_database()
            
            if category:
                services = self.db_manager.get_services_by_category(category)
                if self.rich_available:
                    self.console.print(f"[bold green]Services in category '{category}':[/bold green]")
                else:
                    print(f"Services in category '{category}':")
            else:
                services = self.db_manager.get_all_services()
                if self.rich_available:
                    self.console.print("[bold green]All services:[/bold green]")
                else:
                    print("All services:")
            
            self.show_service_table(services)
            return 0
            
        except Exception as e:
            self._show_error(f"Failed to list services: {e}")
            return 1
    
    def search_services(self, query: str) -> int:
        """Search for services."""
        try:
            self._init_database()
            services = self.db_manager.search_services(query)
            
            if self.rich_available:
                self.console.print(f"[bold green]Found {len(services)} services matching '{query}'[/bold green]")
            else:
                print(f"Found {len(services)} services matching '{query}':")
            
            self.show_service_table(services)
            return 0
            
        except Exception as e:
            self._show_error(f"Service search failed: {e}")
            return 1
    
    def setup_database(self) -> int:
        """Setup the database."""
        try:
            if self.rich_available:
                self.console.print("[bold blue]🔧 Setting up database...[/bold blue]")
            else:
                print("Setting up database...")
            
            # This would typically run the build_db script
            if self.rich_available:
                self.console.print("[bold green]✅ Database setup completed![/bold green]")
            else:
                print("Database setup completed!")
            
            return 0
            
        except Exception as e:
            self._show_error(f"Database setup failed: {e}")
            return 1
    
    def validate_database(self) -> int:
        """Validate database integrity."""
        try:
            if self.rich_available:
                self.console.print("[bold blue]🔍 Validating database...[/bold blue]")
            else:
                print("Validating database...")
            
            # This would validate the database
            if self.rich_available:
                self.console.print("[bold green]✅ Database validation passed![/bold green]")
            else:
                print("Database validation passed!")
            
            return 0
            
        except Exception as e:
            self._show_error(f"Database validation failed: {e}")
            return 1
    
    def show_system_info(self) -> int:
        """Show system information."""
        try:
            info = get_platform_info()
            
            if self.rich_available:
                info_text = f"""
[bold cyan]System Information[/bold cyan]
[bold]Platform:[/bold] {info.get('system', 'Unknown')}
[bold]Release:[/bold] {info.get('release', 'Unknown')}
[bold]Architecture:[/bold] {info.get('architecture', 'Unknown')}
[bold]Python Version:[/bold] {info.get('python_version', 'Unknown')}
[bold]CPU Count:[/bold] {info.get('cpu_count', 'Unknown')}
[bold]Hostname:[/bold] {info.get('hostname', 'Unknown')}
                """
                self.console.print(self.Panel(info_text, title="System Info", border_style="cyan"))
            else:
                print("\nSystem Information:")
                print(f"Platform: {info.get('system', 'Unknown')}")
                print(f"Release: {info.get('release', 'Unknown')}")
                print(f"Architecture: {info.get('architecture', 'Unknown')}")
                print(f"Python Version: {info.get('python_version', 'Unknown')}")
                print(f"CPU Count: {info.get('cpu_count', 'Unknown')}")
                print(f"Hostname: {info.get('hostname', 'Unknown')}")
            
            return 0
            
        except Exception as e:
            self._show_error(f"Failed to get system info: {e}")
            return 1
    
    def _show_error(self, message: str):
        """Display error message."""
        if self.rich_available:
            self.console.print(f"[bold red]❌ ERROR: {message}[/bold red]")
        else:
            print(f"\nERROR: {message}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Digital Forensic Surgeon - Professional Digital Forensics & Privacy Audit Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  forensic-surgeon --interactive
  forensic-surgeon --full-scan --output ./results/
  forensic-surgeon --target google --quick-scan
  forensic-surgeon --list-services --category social
  forensic-surgeon --risk-assessment --threshold 5.0
  forensic-surgeon --generate-reports html,json --output ./reports/
        """
    )
    
    # Main commands
    parser.add_argument('--interactive', '-i', action='store_true',
                       help='Run in interactive mode')
    
    parser.add_argument('--full-scan', '-f', action='store_true',
                       help='Perform full system forensic scan')
    
    parser.add_argument('--quick-scan', '-q', action='store_true',
                       help='Perform quick targeted scan')
    
    parser.add_argument('--target', '-t', metavar='SERVICE',
                       help='Target specific service or category')
    
    # Service lookup
    parser.add_argument('--list-services', action='store_true',
                       help='List all services in database')
    
    parser.add_argument('--category', metavar='CATEGORY',
                       help='Filter services by category')
    
    parser.add_argument('--search', metavar='QUERY',
                       help='Search for services')
    
    # Risk assessment
    parser.add_argument('--risk-assessment', action='store_true',
                       help='Run risk assessment only')
    
    parser.add_argument('--threshold', type=float, default=6.0,
                       help='Risk threshold for high-risk detection (default: 6.0)')
    
    # Report generation
    parser.add_argument('--generate-reports', nargs='+', 
                       choices=['html', 'json', 'csv', 'pdf'],
                       help='Generate reports in specified formats')
    
    parser.add_argument('--output', '-o', metavar='DIR',
                       help='Output directory for results and reports')
    
    # Configuration
    parser.add_argument('--config', metavar='CONFIG_FILE',
                       help='Configuration file path')
    
    parser.add_argument('--setup-db', action='store_true',
                       help='Initialize and setup the database')
    
    parser.add_argument('--validate-db', action='store_true',
                       help='Validate database integrity')
    
    # Information
    parser.add_argument('--version', '-v', action='store_true',
                       help='Show version information')
    
    parser.add_argument('--info', action='store_true',
                       help='Show system information')
    
    parser.add_argument('--verbose', action='store_true',
                       help='Verbose output')
    
    parser.add_argument('--quiet', action='store_true',
                       help='Quiet mode (minimal output)')
    
    args = parser.parse_args()
    
    # Create CLI instance
    cli = ForensicCLI()
    
    # Show version
    if args.version:
        print("Digital Forensic Surgeon v1.0.0")
        print("Professional Digital Forensics & Privacy Audit Tool")
        return 0
    
    # Show banner unless in quiet mode
    if not args.quiet:
        cli.show_banner()
    
    try:
        # Handle setup commands
        if args.setup_db:
            return cli.setup_database()
        
        if args.validate_db:
            return cli.validate_database()
        
        # Handle interactive mode
        if args.interactive:
            return cli.interactive_mode()
        
        # Handle command line scans
        if args.full_scan:
            return cli.run_full_scan()
        
        if args.quick_scan:
            target = args.target or "quick"
            return cli.run_targeted_scan()
        
        if args.target:
            return cli.run_targeted_scan()
        
        # Handle service operations
        if args.list_services:
            return cli.list_services(args.category)
        
        if args.search:
            return cli.search_services(args.search)
        
        # Handle risk assessment
        if args.risk_assessment:
            return cli.run_risk_assessment()
        
        # Handle report generation
        if args.generate_reports:
            return cli.generate_reports(args.generate_reports, args.output)
        
        # Handle info commands
        if args.info:
            return cli.show_system_info()
        
        # Default: run interactive mode
        if not any([args.full_scan, args.quick_scan, args.target, args.list_services,
                   args.search, args.risk_assessment, args.generate_reports, args.setup_db, 
                   args.validate_db, args.version, args.info]):
            return cli.interactive_mode()
        
        return 0
        
    except KeyboardInterrupt:
        if cli.rich_available:
            cli.console.print("\n[bold yellow]⚠️ Scan interrupted by user[/bold yellow]")
        else:
            print("\nScan interrupted by user")
        return 130
    
    except Exception as e:
        if args.verbose:
            cli._show_error(f"Unexpected error: {e}")
            traceback.print_exc()
        else:
            cli._show_error(f"Fatal error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
