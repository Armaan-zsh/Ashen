"""
Interactive Real-time Forensic Dashboard
Provides comprehensive visualization and monitoring of forensic analysis results
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import asdict
import threading
from collections import defaultdict, deque
from pathlib import Path

try:
    from fastapi import FastAPI, WebSocket, WebSocketDisconnect
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import HTMLResponse
    from fastapi.middleware.cors import CORSMiddleware
    import uvicorn
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

from ..core.models import EvidenceItem, ForensicResult
from ..core.config import ForensicConfig
from ..scanners.packet_analyzer import PacketDataAnalyzer
from ..scanners.content_classifier import DataContentClassifier
from ..scanners.destination_intelligence import DestinationIntelligence
from ..scanners.application_monitor import ApplicationNetworkMonitor
from ..scanners.security_auditor import AccountSecurityAuditor
from ..scanners.behavioral_intelligence import BehavioralIntelligenceEngine

class ForensicDashboard:
    """Interactive real-time forensic analysis dashboard"""
    
    def __init__(self, config: Optional[ForensicConfig] = None):
        self.config = config or ForensicConfig()
        self.scanners = self._init_scanners()
        self.active_connections = set()
        self.real_time_data = deque(maxlen=1000)
        self.alert_queue = deque(maxlen=100)
        self.monitoring_active = False
        self.monitoring_thread = None
        
        # Dashboard state
        self.dashboard_state = {
            'last_update': datetime.now().isoformat(),
            'total_evidence': 0,
            'high_risk_items': 0,
            'active_monitors': 0,
            'system_status': 'ready',
            'alerts': []
        }
        
        # Initialize FastAPI app if available
        if FASTAPI_AVAILABLE:
            self.app = self._create_app()
        else:
            self.app = None
    
    def _init_scanners(self) -> Dict[str, Any]:
        """Initialize all scanners"""
        return {
            'packet_analyzer': PacketDataAnalyzer(self.config),
            'content_classifier': DataContentClassifier(self.config),
            'destination_intelligence': DestinationIntelligence(self.config),
            'application_monitor': ApplicationNetworkMonitor(self.config),
            'security_auditor': AccountSecurityAuditor(self.config),
            'behavioral_engine': BehavioralIntelligenceEngine(self.config)
        }
    
    def _create_app(self) -> FastAPI:
        """Create FastAPI application"""
        app = FastAPI(title="Forensic Dashboard", version="1.0.0")
        
        # Add CORS middleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # WebSocket endpoint for real-time updates
        @app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await websocket.accept()
            self.active_connections.add(websocket)
            try:
                while True:
                    # Send real-time data
                    await self._send_real_time_update(websocket)
                    await asyncio.sleep(1)  # Update every second
            except WebSocketDisconnect:
                self.active_connections.remove(websocket)
        
        # API endpoints
        @app.get("/api/status")
        async def get_status():
            return {
                'total_evidence': self.dashboard_state.get('total_evidence', 0),
                'high_risk_items': self.dashboard_state.get('high_risk_items', 0),
                'active_monitors': self.dashboard_state.get('active_monitors', 0),
                'system_status': self.dashboard_state.get('system_status', 'ready'),
                'last_update': self.dashboard_state.get('last_update', datetime.now().isoformat()),
                'alerts': self.dashboard_state.get('alerts', [])
            }
        
        @app.get("/api/evidence")
        async def get_evidence():
            return {
                'recent_evidence': list(self.real_time_data)[-50:],
                'total_count': len(self.real_time_data)
            }
        
        @app.get("/api/alerts")
        async def get_alerts():
            return {
                'alerts': list(self.alert_queue),
                'alert_count': len(self.alert_queue)
            }
        
        @app.post("/api/start_monitoring")
        async def start_monitoring():
            if not self.monitoring_active:
                self._start_monitoring()
                return {"status": "monitoring_started"}
            return {"status": "already_monitoring"}
        
        @app.post("/api/stop_monitoring")
        async def stop_monitoring():
            if self.monitoring_active:
                self._stop_monitoring()
                return {"status": "monitoring_stopped"}
            return {"status": "not_monitoring"}
        
        @app.get("/api/scan_results/{scan_type}")
        async def get_scan_results(scan_type: str):
            return await self._get_scan_results(scan_type)
        
        @app.post("/api/run_scan/{scan_type}")
        async def run_scan(scan_type: str, params: Dict[str, Any] = None):
            return await self._run_scan(scan_type, params or {})
        
        # Mount static files
        static_dir = Path(__file__).parent / "static"
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
        
        # Main dashboard page
        @app.get("/", response_class=HTMLResponse)
        async def dashboard_page():
            return self._get_dashboard_html()
        
        return app
    
    async def _send_real_time_update(self, websocket: WebSocket):
        """Send real-time update to WebSocket client"""
        try:
            update_data = {
                'timestamp': datetime.now().isoformat(),
                'evidence_count': len(self.real_time_data),
                'alert_count': len(self.alert_queue),
                'system_status': self.dashboard_state['system_status'],
                'recent_evidence': list(self.real_time_data)[-5:],
                'recent_alerts': list(self.alert_queue)[-3:]
            }
            await websocket.send_json(update_data)
        except Exception as e:
            print(f"Error sending WebSocket update: {e}")
    
    def _start_monitoring(self):
        """Start real-time monitoring"""
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        self.dashboard_state['active_monitors'] += 1
        self.dashboard_state['system_status'] = 'monitoring'
    
    def _stop_monitoring(self):
        """Stop real-time monitoring"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        self.dashboard_state['active_monitors'] = max(0, self.dashboard_state['active_monitors'] - 1)
        self.dashboard_state['system_status'] = 'ready'
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                # Run various scans and collect evidence
                self._collect_packet_evidence()
                self._collect_application_evidence()
                self._check_for_alerts()
                
                # Update dashboard state
                self.dashboard_state['last_update'] = datetime.now().isoformat()
                self.dashboard_state['total_evidence'] = len(self.real_time_data)
                self.dashboard_state['high_risk_items'] = len([
                    e for e in self.real_time_data 
                    if e.get('severity') in ['critical', 'high'] or e.get('is_sensitive', False)
                ])
                
                time.sleep(5)  # Monitor every 5 seconds
                
            except Exception as e:
                print(f"Error in monitoring loop: {e}")
                time.sleep(10)
    
    def _collect_packet_evidence(self):
        """Collect packet analysis evidence"""
        try:
            packet_analyzer = self.scanners['packet_analyzer']
            # Run a quick packet scan
            evidence_items = list(packet_analyzer.analyze_network_packets(
                interface_filter="any", 
                duration_seconds=5
            ))
            
            for evidence in evidence_items:
                evidence_data = asdict(evidence)
                evidence_data['collection_time'] = datetime.now().isoformat()
                # Add severity from metadata if available, otherwise default to 'low'
                severity = evidence_data.get('metadata', {}).get('severity', 'low')
                evidence_data['severity'] = severity
                # Use content as description
                evidence_data['description'] = evidence_data.get('content', 'No description')
                self.real_time_data.append(evidence_data)
                
                # Check for alerts based on metadata or is_sensitive flag
                if severity in ['critical', 'high'] or evidence.is_sensitive:
                    self._add_alert(
                        f"High severity packet activity: {evidence_data['description']}",
                        severity,
                        'packet_analysis'
                    )
                    
        except Exception as e:
            print(f"Error collecting packet evidence: {e}")
    
    def _collect_application_evidence(self):
        """Collect application monitoring evidence"""
        try:
            app_monitor = self.scanners['application_monitor']
            
            # Get current network connections
            connections = app_monitor._get_network_connections()
            
            for connection in connections:
                if connection.risk_score > 7.0:
                    evidence_data = asdict(connection)
                    evidence_data['collection_time'] = datetime.now().isoformat()
                    self.real_time_data.append(evidence_data)
                    
                    self._add_alert(
                        f"Suspicious application activity: {connection.process_name}",
                        'high',
                        'application_monitoring'
                    )
                    
        except Exception as e:
            print(f"Error collecting application evidence: {e}")
    
    def _check_for_alerts(self):
        """Check for alert conditions"""
        # Check evidence rate
        recent_evidence = [
            e for e in self.real_time_data 
            if datetime.fromisoformat(e['collection_time']) > datetime.now() - timedelta(minutes=5)
        ]
        
        if len(recent_evidence) > 50:
            self._add_alert(
                "High evidence generation rate detected",
                'medium',
                'system_monitoring'
            )
        
        # Check for repeated high-risk patterns
        high_risk_sources = defaultdict(int)
        for evidence in recent_evidence:
            if evidence.get('severity') in ['critical', 'high']:
                high_risk_sources[evidence.get('source', 'unknown')] += 1
        
        for source, count in high_risk_sources.items():
            if count > 10:
                self._add_alert(
                    f"Multiple high-risk events from {source}",
                    'high',
                    'pattern_analysis'
                )
    
    def _add_alert(self, message: str, severity: str, alert_type: str):
        """Add alert to queue"""
        alert = {
            'id': f"alert_{int(time.time())}_{len(self.alert_queue)}",
            'message': message,
            'severity': severity,
            'type': alert_type,
            'timestamp': datetime.now().isoformat()
        }
        self.alert_queue.append(alert)
        self.dashboard_state['alerts'].append(alert)
        
        # Keep only recent alerts in dashboard state
        if len(self.dashboard_state['alerts']) > 20:
            self.dashboard_state['alerts'] = self.dashboard_state['alerts'][-20:]
    
    async def _get_scan_results(self, scan_type: str) -> Dict[str, Any]:
        """Get results for specific scan type"""
        try:
            if scan_type == 'packet':
                analyzer = self.scanners['packet_analyzer']
                # Return recent packet analysis results
                return {
                    'scan_type': scan_type,
                    'results': [e for e in self.real_time_data if e.get('source') == 'packet_analyzer'][-20:],
                    'summary': self._generate_packet_summary()
                }
            elif scan_type == 'content':
                classifier = self.scanners['content_classifier']
                return {
                    'scan_type': scan_type,
                    'results': [e for e in self.real_time_data if e.get('source') == 'content_classifier'][-20:],
                    'summary': self._generate_content_summary()
                }
            elif scan_type == 'destination':
                dest_analyzer = self.scanners['destination_intelligence']
                return {
                    'scan_type': scan_type,
                    'results': [e for e in self.real_time_data if e.get('source') == 'destination_intelligence'][-20:],
                    'summary': self._generate_destination_summary()
                }
            elif scan_type == 'application':
                app_monitor = self.scanners['application_monitor']
                return {
                    'scan_type': scan_type,
                    'results': [e for e in self.real_time_data if e.get('source') == 'application_monitor'][-20:],
                    'summary': self._generate_application_summary()
                }
            elif scan_type == 'security':
                auditor = self.scanners['security_auditor']
                return {
                    'scan_type': scan_type,
                    'results': [e for e in self.real_time_data if e.get('source') == 'security_auditor'][-20:],
                    'summary': self._generate_security_summary()
                }
            elif scan_type == 'behavioral':
                behavioral = self.scanners['behavioral_engine']
                return {
                    'scan_type': scan_type,
                    'results': [e for e in self.real_time_data if e.get('source') == 'behavioral_intelligence'][-20:],
                    'summary': self._generate_behavioral_summary()
                }
            else:
                return {'error': f'Unknown scan type: {scan_type}'}
                
        except Exception as e:
            return {'error': str(e)}
    
    async def _run_scan(self, scan_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Run a specific scan with parameters"""
        try:
            if scan_type == 'packet':
                analyzer = self.scanners['packet_analyzer']
                evidence_items = list(analyzer.scan())
                return {'results': [asdict(e) for e in evidence_items], 'count': len(evidence_items)}
                
            elif scan_type == 'content':
                classifier = self.scanners['content_classifier']
                evidence_items = list(classifier.scan())
                return {'results': [asdict(e) for e in evidence_items], 'count': len(evidence_items)}
                
            elif scan_type == 'destination':
                dest_analyzer = self.scanners['destination_intelligence']
                evidence_items = list(dest_analyzer.scan())
                return {'results': [asdict(e) for e in evidence_items], 'count': len(evidence_items)}
                
            elif scan_type == 'application':
                app_monitor = self.scanners['application_monitor']
                evidence_items = list(app_monitor.scan())
                return {'results': [asdict(e) for e in evidence_items], 'count': len(evidence_items)}
                
            elif scan_type == 'security':
                auditor = self.scanners['security_auditor']
                evidence_items = list(auditor.scan())
                return {'results': [asdict(e) for e in evidence_items], 'count': len(evidence_items)}
                
            elif scan_type == 'behavioral':
                behavioral = self.scanners['behavioral_engine']
                evidence_items = list(behavioral.scan())
                return {'results': [asdict(e) for e in evidence_items], 'count': len(evidence_items)}
                
            else:
                return {'error': f'Unknown scan type: {scan_type}'}
                
        except Exception as e:
            return {'error': str(e)}
    
    def _generate_packet_summary(self) -> Dict[str, Any]:
        """Generate packet analysis summary"""
        packet_evidence = [e for e in self.real_time_data if e.get('source') == 'packet_analyzer']
        
        if not packet_evidence:
            return {'message': 'No packet evidence available'}
        
        return {
            'total_packets': len(packet_evidence),
            'high_risk_packets': len([e for e in packet_evidence if e.get('severity') in ['critical', 'high']]),
            'protocols': defaultdict(int),
            'top_sources': defaultdict(int),
            'time_range': {
                'start': min(e.get('collection_time') for e in packet_evidence),
                'end': max(e.get('collection_time') for e in packet_evidence)
            }
        }
    
    def _generate_content_summary(self) -> Dict[str, Any]:
        """Generate content classification summary"""
        content_evidence = [e for e in self.real_time_data if e.get('source') == 'content_classifier']
        
        if not content_evidence:
            return {'message': 'No content evidence available'}
        
        return {
            'total_files': len(content_evidence),
            'pii_files': len([e for e in content_evidence if 'pii' in e.get('data_type', '').lower()]),
            'behavioral_files': len([e for e in content_evidence if 'behavioral' in e.get('data_type', '').lower()]),
            'file_types': defaultdict(int),
            'risk_levels': defaultdict(int)
        }
    
    def _generate_destination_summary(self) -> Dict[str, Any]:
        """Generate destination intelligence summary"""
        dest_evidence = [e for e in self.real_time_data if e.get('source') == 'destination_intelligence']
        
        if not dest_evidence:
            return {'message': 'No destination evidence available'}
        
        return {
            'total_destinations': len(dest_evidence),
            'high_risk_destinations': len([e for e in dest_evidence if e.get('severity') in ['critical', 'high']]),
            'categories': defaultdict(int),
            'countries': defaultdict(int)
        }
    
    def _generate_application_summary(self) -> Dict[str, Any]:
        """Generate application monitoring summary"""
        app_evidence = [e for e in self.real_time_data if e.get('source') == 'application_monitor']
        
        if not app_evidence:
            return {'message': 'No application evidence available'}
        
        return {
            'total_applications': len(set(e.get('process_name') for e in app_evidence)),
            'high_risk_applications': len([e for e in app_evidence if e.get('risk_score', 0) > 7.0]),
            'connection_types': defaultdict(int),
            'top_applications': defaultdict(int)
        }
    
    def _generate_security_summary(self) -> Dict[str, Any]:
        """Generate security audit summary"""
        security_evidence = [e for e in self.real_time_data if e.get('source') == 'security_auditor']
        
        if not security_evidence:
            return {'message': 'No security evidence available'}
        
        return {
            'total_findings': len(security_evidence),
            'vulnerabilities': len([e for e in security_evidence if 'vulnerability' in e.get('data_type', '').lower()]),
            'recommendations': len([e for e in security_evidence if 'recommendation' in e.get('data_type', '').lower()]),
            'risk_levels': defaultdict(int)
        }
    
    def _generate_behavioral_summary(self) -> Dict[str, Any]:
        """Generate behavioral intelligence summary"""
        behavioral_evidence = [e for e in self.real_time_data if e.get('source') == 'behavioral_intelligence']
        
        if not behavioral_evidence:
            return {'message': 'No behavioral evidence available'}
        
        return {
            'total_patterns': len([e for e in behavioral_evidence if 'pattern' in e.get('data_type', '').lower()]),
            'total_anomalies': len([e for e in behavioral_evidence if 'anomaly' in e.get('data_type', '').lower()]),
            'risk_levels': defaultdict(int),
            'entity_types': defaultdict(int)
        }
    
    def _get_dashboard_html(self) -> str:
        """Generate dashboard HTML"""
        return """
<!DOCTYPE html>
<html>
<head>
    <title>Forensic Dashboard</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }
        .header { background: #2c3e50; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .dashboard-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .card h3 { margin-top: 0; color: #2c3e50; }
        .metric { font-size: 2em; font-weight: bold; color: #3498db; }
        .alert { background: #e74c3c; color: white; padding: 10px; border-radius: 4px; margin: 5px 0; }
        .alert.medium { background: #f39c12; }
        .alert.low { background: #27ae60; }
        .status-indicator { display: inline-block; width: 12px; height: 12px; border-radius: 50%; margin-right: 8px; }
        .status-ready { background: #27ae60; }
        .status-monitoring { background: #3498db; }
        .status-error { background: #e74c3c; }
        .button { background: #3498db; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; margin: 5px; }
        .button:hover { background: #2980b9; }
        .evidence-list { max-height: 300px; overflow-y: auto; }
        .evidence-item { background: #ecf0f1; padding: 10px; margin: 5px 0; border-radius: 4px; font-size: 0.9em; }
        .chart-container { position: relative; height: 200px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Digital Forensic Dashboard</h1>
        <div>
            <span class="status-indicator status-ready" id="status-indicator"></span>
            <span id="status-text">Ready</span>
            <span style="float: right;" id="last-update">Last Update: Never</span>
        </div>
    </div>

    <div class="dashboard-grid">
        <!-- System Status Card -->
        <div class="card">
            <h3>System Status</h3>
            <div class="metric" id="total-evidence">0</div>
            <p>Total Evidence Items</p>
            <div class="metric" id="high-risk-items">0</div>
            <p>High Risk Items</p>
            <button class="button" onclick="toggleMonitoring(this)">Start Monitoring</button>
            <button class="button" onclick="runScan('packet', this)">Run Packet Scan</button>
        </div>

        <!-- Alerts Card -->
        <div class="card">
            <h3>Recent Alerts</h3>
            <div class="metric" id="alert-count">0</div>
            <p>Active Alerts</p>
            <div id="alerts-container"></div>
        </div>

        <!-- Evidence Timeline -->
        <div class="card">
            <h3>Recent Evidence</h3>
            <div class="evidence-list" id="evidence-container"></div>
        </div>

        <!-- Charts -->
        <div class="card">
            <h3>Evidence Distribution</h3>
            <div class="chart-container">
                <canvas id="evidence-chart"></canvas>
            </div>
        </div>

        <div class="card">
            <h3>Risk Level Distribution</h3>
            <div class="chart-container">
                <canvas id="risk-chart"></canvas>
            </div>
        </div>

        <!-- Scan Controls -->
        <div class="card">
            <h3>Scan Controls</h3>
            <button class="button" onclick="runScan('packet', this)">Packet Analysis</button>
            <button class="button" onclick="runScan('content', this)">Content Classification</button>
            <button class="button" onclick="runScan('destination', this)">Destination Intelligence</button>
            <button class="button" onclick="runScan('application', this)">Application Monitoring</button>
            <button class="button" onclick="runScan('security', this)">Security Audit</button>
            <button class="button" onclick="runScan('behavioral', this)">Behavioral Analysis</button>
        </div>
    </div>

    <script src="/static/script.js"></script>
    <script>
        let ws = null;
        let monitoring = false;
        let evidenceChart = null;
        let riskChart = null;

        // Initialize WebSocket connection
        function initWebSocket() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            ws = new WebSocket(`${protocol}//${window.location.host}/ws`);
            
            ws.onopen = function() {
                console.log('WebSocket connected');
                updateStatus('monitoring');
            };
            
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                updateDashboard(data);
            };
            
            ws.onclose = function() {
                console.log('WebSocket disconnected');
                updateStatus('error');
                // Try to reconnect after 5 seconds
                setTimeout(initWebSocket, 5000);
            };
            
            ws.onerror = function(error) {
                console.error('WebSocket error:', error);
                updateStatus('error');
            };
        }

        // Update dashboard with real-time data
        function updateDashboard(data) {
            document.getElementById('total-evidence').textContent = data.evidence_count || 0;
            document.getElementById('high-risk-items').textContent = 
                (data.recent_evidence || []).filter(e => e.severity === 'critical' || e.severity === 'high').length;
            document.getElementById('alert-count').textContent = data.alert_count || 0;
            document.getElementById('last-update').textContent = `Last Update: ${new Date(data.timestamp).toLocaleTimeString()}`;
            
            // Update alerts
            const alertsContainer = document.getElementById('alerts-container');
            if (alertsContainer) {
                alertsContainer.innerHTML = '';
                (data.recent_alerts || []).forEach(alert => {
                    const alertDiv = document.createElement('div');
                    alertDiv.className = `alert ${alert.severity || 'low'}`;
                    alertDiv.textContent = alert.message || alert;
                    alertsContainer.appendChild(alertDiv);
                });
            }
            
            // Update evidence
            const evidenceContainer = document.getElementById('evidence-container');
            if (evidenceContainer) {
                evidenceContainer.innerHTML = '';
                (data.recent_evidence || []).forEach(evidence => {
                    const evidenceDiv = document.createElement('div');
                    evidenceDiv.className = 'evidence-item';
                    const source = evidence.source || evidence.get?.('source') || 'Unknown';
                    const description = evidence.description || evidence.content || evidence.get?.('content') || 'No description';
                    evidenceDiv.innerHTML = `<strong>${source}</strong>: ${description}`;
                    evidenceContainer.appendChild(evidenceDiv);
                });
            }
            
            // Update charts
            updateCharts(data);
        }

        // Update status indicator
        function updateStatus(status) {
            const indicator = document.getElementById('status-indicator');
            const text = document.getElementById('status-text');
            
            if (indicator) {
                indicator.className = `status-indicator status-${status}`;
            }
            if (text) {
                switch(status) {
                    case 'ready':
                        text.textContent = 'Ready';
                        break;
                    case 'monitoring':
                        text.textContent = 'Monitoring';
                        break;
                    case 'error':
                        text.textContent = 'Error';
                        break;
                }
            }
        }

        // Initialize charts
        function initCharts() {
            const evidenceCanvas = document.getElementById('evidence-chart');
            const riskCanvas = document.getElementById('risk-chart');
            
            if (evidenceCanvas) {
                const evidenceCtx = evidenceCanvas.getContext('2d');
                evidenceChart = new Chart(evidenceCtx, {
                    type: 'doughnut',
                    data: {
                        labels: ['Packet', 'Content', 'Destination', 'Application', 'Security', 'Behavioral'],
                        datasets: [{
                            data: [0, 0, 0, 0, 0, 0],
                            backgroundColor: ['#3498db', '#e74c3c', '#f39c12', '#27ae60', '#9b59b6', '#1abc9c']
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false
                    }
                });
            }

            if (riskCanvas) {
                const riskCtx = riskCanvas.getContext('2d');
                riskChart = new Chart(riskCtx, {
                    type: 'bar',
                    data: {
                        labels: ['Low', 'Medium', 'High', 'Critical'],
                        datasets: [{
                            label: 'Risk Level Distribution',
                            data: [0, 0, 0, 0],
                            backgroundColor: ['#27ae60', '#f39c12', '#e67e22', '#e74c3c']
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {
                            y: {
                                beginAtZero: true
                            }
                        }
                    }
                });
            }
        }

        // Update charts with data
        function updateCharts(data) {
            if (evidenceChart && riskChart) {
                // Update evidence distribution (mock data for now)
                evidenceChart.data.datasets[0].data = [
                    Math.floor(Math.random() * 10),
                    Math.floor(Math.random() * 10),
                    Math.floor(Math.random() * 10),
                    Math.floor(Math.random() * 10),
                    Math.floor(Math.random() * 10),
                    Math.floor(Math.random() * 10)
                ];
                evidenceChart.update();

                // Update risk distribution
                const riskLevels = (data.recent_evidence || []).reduce((acc, e) => {
                    const severity = e.severity || 'low';
                    acc[severity] = (acc[severity] || 0) + 1;
                    return acc;
                }, {});
                
                riskChart.data.datasets[0].data = [
                    riskLevels.low || 0,
                    riskLevels.medium || 0,
                    riskLevels.high || 0,
                    riskLevels.critical || 0
                ];
                riskChart.update();
            }
        }

        // Initialize dashboard
        document.addEventListener('DOMContentLoaded', function() {
            initWebSocket();
            initCharts();
            
            // Load initial data
            fetch('/api/status').then(response => response.json()).then(data => {
                const totalEvidenceEl = document.getElementById('total-evidence');
                const highRiskEl = document.getElementById('high-risk-items');
                if (totalEvidenceEl) {
                    totalEvidenceEl.textContent = data.total_evidence || 0;
                }
                if (highRiskEl) {
                    highRiskEl.textContent = data.high_risk_items || 0;
                }
            }).catch(error => {
                console.error('Failed to load initial status:', error);
            });
        });
    </script>
</body>
</html>
"""
    
def start_dashboard(host: str = "127.0.0.1", port: int = 8001):
    """Start the dashboard server"""
    if not FASTAPI_AVAILABLE:
        print("FastAPI not available. Please install with: pip install fastapi uvicorn")
        return
    
    dashboard = ForensicDashboard()
    uvicorn.run(dashboard.app, host=host, port=port)

# Global dashboard instance
_dashboard_instance = None

def get_dashboard(config: Optional[ForensicConfig] = None) -> ForensicDashboard:
    """Get or create dashboard instance"""
    global _dashboard_instance
    if _dashboard_instance is None:
        _dashboard_instance = ForensicDashboard(config)
    return _dashboard_instance

if __name__ == "__main__":
    # Run dashboard directly
    start_dashboard()
