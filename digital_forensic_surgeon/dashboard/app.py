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
import uvicorn

try:
    from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, Form, HTTPException
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import HTMLResponse
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.templating import Jinja2Templates
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

from ..core.models import EvidenceItem, ForensicResult
from ..core.config import get_config, ForensicConfig
from ..scanners.packet_analyzer import PacketDataAnalyzer
from ..scanners.network.wifi import WiFiScanner
from ..scanners.filesystem import FileSystemScanner
from ..scanners.osint import OSINTScanner
from ..scanners.browser.cleaner import BrowserCleaner
from ..db.manager import DatabaseManager
from ..db.schema import initialize_schema


class ForensicDashboard:
    """Interactive real-time forensic analysis dashboard"""
    
    def __init__(self, config: Optional[ForensicConfig] = None):
        self.config = config or get_config()
        
        # Initialize Database
        self.db = DatabaseManager(self.config.db_path)
        with self.db.get_connection() as conn:
            initialize_schema(conn)
            
        # Initialize scanners
        self.packet_analyzer = PacketDataAnalyzer(self.config)
        self.wifi_scanner = WiFiScanner(self.config)
        self.fs_scanner = FileSystemScanner(self.config)
        self.osint_scanner = OSINTScanner(self.config)
        
        self.active_connections = set()
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
    
    def _create_app(self) -> "FastAPI":
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
            # Get stats from DB
            recent_evidence = self.db.get_recent_evidence(limit=1000)
            high_risk_count = len([
                e for e in recent_evidence
                if e.get('severity') in ['critical', 'high'] or e.get('is_sensitive', False)
            ])
            
            return {
                'total_evidence': len(recent_evidence), # Approximation for now
                'high_risk_items': high_risk_count,
                'active_monitors': self.dashboard_state.get('active_monitors', 0),
                'system_status': self.dashboard_state.get('system_status', 'ready'),
                'last_update': self.dashboard_state.get('last_update', datetime.now().isoformat()),
                'alerts': list(self.alert_queue)
            }
        
        @app.get("/api/evidence")
        async def get_evidence(limit: int = 50):
            recent = self.db.get_recent_evidence(limit=limit)
            return {
                'recent_evidence': recent,
                'total_count': len(recent)
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
        
        @app.post("/api/run_scan/{scan_type}")
        async def run_scan(scan_type: str, params: Dict[str, Any] = None):
            return await self._run_scan(scan_type, params or {})

        @app.post("/api/amputate")
        async def amputate_service(service_name: str = Form(...)):
            """
            The 'Kill Switch'.
            1. Kills active sessions for this service.
            2. Wipes specific cookies/local storage.
            3. Adds domain to local blocklist (optional).
            """
            try:
                cleaner = BrowserCleaner()
                results = cleaner.nuke_site_data(service_name)
                return {"status": "Amputation Successful", "details": results}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        # Mount static files
        static_dir = Path(__file__).parent / "static"
        static_dir.mkdir(exist_ok=True)
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
        
        # Main dashboard page
        @app.get("/", response_class=HTMLResponse)
        async def dashboard_page():
            return self._get_dashboard_html()
        
        return app
    
    async def _send_real_time_update(self, websocket: WebSocket):
        """Send real-time update to WebSocket client"""
        try:
            recent_evidence = self.db.get_recent_evidence(limit=10)
            
            update_data = {
                'timestamp': datetime.now().isoformat(),
                'evidence_count': len(recent_evidence), # Just showing recent count for now
                'alert_count': len(self.alert_queue),
                'system_status': self.dashboard_state['system_status'],
                'recent_evidence': recent_evidence,
                'recent_alerts': [
                    {**a, 'timestamp': a['timestamp'] if isinstance(a.get('timestamp'), str) else a.get('timestamp').isoformat()}
                    for a in list(self.alert_queue)[-3:]
                ]
            }
            await websocket.send_json(update_data)
        except Exception as e:
            print(f"Error sending WebSocket update: {e}")
    
    def _start_monitoring(self):
        """Start real-time monitoring"""
        if self.monitoring_active:
            return
            
        self.monitoring_active = True
        
        # Start Packet Analyzer Background Daemon
        self.packet_analyzer.start_monitoring()
        
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        self.dashboard_state['active_monitors'] = 1
        self.dashboard_state['system_status'] = 'monitoring'
    
    def _stop_monitoring(self):
        """Stop real-time monitoring"""
        self.monitoring_active = False
        self.packet_analyzer.stop_monitoring()
        
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=2.0)
            
        self.dashboard_state['active_monitors'] = 0
        self.dashboard_state['system_status'] = 'ready'
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                # Run various scans and collect evidence
                self._collect_packet_evidence()
                self._check_for_alerts()
                
                # Update dashboard state
                self.dashboard_state['last_update'] = datetime.now().isoformat()
                
                time.sleep(2)  # Monitor every 2 seconds
                
            except Exception as e:
                print(f"Error in monitoring loop: {e}")
                time.sleep(5)
    
    def _collect_packet_evidence(self):
        """Collect packet analysis evidence from background daemon"""
        try:
            # Packet analyzer is running in background, we just need to pull from it
            # The scan() method now yields from the queue if monitoring is active
            for evidence in self.packet_analyzer.scan():
                # Convert EvidenceItem to dict for DB
                evidence_dict = asdict(evidence)
                evidence_dict['timestamp'] = evidence.timestamp.isoformat()
                
                # Add to DB
                self.db.add_evidence(evidence_dict)
                
                # Check for alerts
                severity = evidence.metadata.get('severity', 'low')
                if severity in ['critical', 'high'] or evidence.is_sensitive:
                    self._add_alert(
                        f"High severity packet activity: {evidence.content}",
                        severity,
                        'packet_analysis'
                    )
                    
        except Exception as e:
            print(f"Error collecting packet evidence: {e}")
    
    def _check_for_alerts(self):
        """Check for alert conditions"""
        # Simple check for now
        pass
    
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

    async def _run_scan(self, scan_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Run a specific scan with parameters"""
        try:
            if scan_type == 'packet':
                # Packet scan is continuous, but we can trigger a manual snapshot if needed
                # For now, just return recent evidence
                recent = self.db.get_recent_evidence(limit=50)
                packet_evidence = [e for e in recent if e['source'] == 'packet_analyzer']
                return {'results': packet_evidence, 'count': len(packet_evidence)}
                
            elif scan_type == 'osint':
                username = params.get('username')
                if not username:
                    return {'error': 'Username required for OSINT scan'}
                
                # Use the async method to avoid blocking
                evidence_items = await self.osint_scanner.scan_username_async(username)
                
                # Store in DB
                for evidence in evidence_items:
                    evidence_dict = asdict(evidence)
                    evidence_dict['timestamp'] = evidence.timestamp.isoformat()
                    self.db.add_evidence(evidence_dict)
                    
                return {'results': [asdict(e) for e in evidence_items], 'count': len(evidence_items)}
                
            elif scan_type == 'wifi':
                # WiFi scanner is sync, might block slightly but usually fast
                # Ideally should be async too, but for now wrap in thread if needed
                # Or just run it (it has sleep inside, so it might block)
                # Let's run it in a thread executor
                loop = asyncio.get_event_loop()
                networks = await loop.run_in_executor(None, self.wifi_scanner.scan_wifi_networks)
                
                results = []
                for net in networks:
                    results.append(asdict(net))
                    
                return {'results': results, 'count': len(results)}
                
            else:
                return {'error': f'Unknown scan type: {scan_type}'}
                
        except Exception as e:
            return {'error': str(e)}
            
    def _get_dashboard_html(self) -> str:
        """Generate dashboard HTML"""
        # Return a simple HTML for now, or load from template if available
        # For brevity, I'll return the existing HTML structure but simplified
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
            <button class="button" onclick="toggleMonitoring()">Start/Stop Monitoring</button>
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
    </div>

    <script>
        let ws = null;
        let monitoring = false;

        function initWebSocket() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            ws = new WebSocket(`${protocol}//${window.location.host}/ws`);
            
            ws.onopen = function() {
                console.log('WebSocket connected');
                document.getElementById('status-text').textContent = 'Connected';
            };
            
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                updateDashboard(data);
            };
            
            ws.onclose = function() {
                console.log('WebSocket disconnected');
                setTimeout(initWebSocket, 5000);
            };
        }

        function updateDashboard(data) {
            document.getElementById('total-evidence').textContent = data.evidence_count || 0;
            document.getElementById('alert-count').textContent = data.alert_count || 0;
            document.getElementById('last-update').textContent = `Last Update: ${new Date(data.timestamp).toLocaleTimeString()}`;
            
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
            
            const evidenceContainer = document.getElementById('evidence-container');
            if (evidenceContainer) {
                evidenceContainer.innerHTML = '';
                (data.recent_evidence || []).forEach(evidence => {
                    const evidenceDiv = document.createElement('div');
                    evidenceDiv.className = 'evidence-item';
                    const source = evidence.source || 'Unknown';
                    const content = evidence.content || 'No content';
                    evidenceDiv.innerHTML = `<strong>${source}</strong>: ${content}`;
                    evidenceContainer.appendChild(evidenceDiv);
                });
            }
        }

        function toggleMonitoring() {
            const endpoint = monitoring ? '/api/stop_monitoring' : '/api/start_monitoring';
            fetch(endpoint, { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    console.log(data);
                    monitoring = !monitoring;
                });
        }

        document.addEventListener('DOMContentLoaded', function() {
            initWebSocket();
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

if __name__ == "__main__":
    start_dashboard()
