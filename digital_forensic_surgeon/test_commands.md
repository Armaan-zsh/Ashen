# Digital Forensic Surgeon - Beast Upgrade Testing Commands

## 🚀 Complete Testing Guide

### 1. **Setup & Installation**
```bash
# Install package in development mode
pip install -e .

# Setup database
forensic-surgeon --setup-db

# Check version
forensic-surgeon --version
```

### 2. **Core Scanner Tests**
```bash
# Test filesystem scanner
forensic-surgeon scan filesystem --paths "C:\Users\shaik\Documents" --output test_filesystem.json

# Test browser scanner  
forensic-surgeon scan browser --output test_browser.json

# Test network scanner
forensic-surgeon scan network --output test_network.json

# Test credential scanner
forensic-surgeon scan credentials --output test_credentials.json

# Test OSINT scanner
forensic-surgeon scan osint --username testuser --output test_osint.json
```

### 3. **Beast Upgrade Component Tests**

#### 3.1 Packet Analyzer Test
```python
# Test packet analyzer directly
python -c "
from digital_forensic_surgeon.scanners.packet_analyzer import PacketAnalyzer
analyzer = PacketAnalyzer()
result = list(analyzer.scan_network_packets(duration=10))
print(f'Packet Analyzer: Found {len(result)} packets')
"
```

#### 3.2 Data Content Classifier Test
```python
# Test content classifier
python -c "
from digital_forensic_surgeon.scanners.content_classifier import DataContentClassifier
classifier = DataContentClassifier()
result = list(classifier.scan_content_classification(['C:\\Users\\shaik\\Documents']))
print(f'Content Classifier: Found {len(result)} classified items')
"
```

#### 3.3 Destination Intelligence Test
```python
# Test destination intelligence
python -c "
from digital_forensic_surgeon.scanners.destination_intelligence import DestinationIntelligence
intel = DestinationIntelligence()
result = list(intel.scan_destination_analysis(['google.com', 'facebook.com']))
print(f'Destination Intelligence: Analyzed {len(result)} destinations')
"
```

#### 3.4 Application Network Monitor Test
```python
# Test application monitor
python -c "
from digital_forensic_surgeon.scanners.application_monitor import ApplicationNetworkMonitor
monitor = ApplicationNetworkMonitor()
result = list(monitor.scan_application_network_activity())
print(f'Application Monitor: Found {len(result)} network activities')
"
```

#### 3.5 Account Security Auditor Test
```python
# Test security auditor
python -c "
from digital_forensic_surgeon.scanners.security_auditor import AccountSecurityAuditor
auditor = AccountSecurityAuditor()
result = list(auditor.scan_account_security())
print(f'Security Auditor: Found {len(result)} security issues')
"
```

#### 3.6 Behavioral Intelligence Test
```python
# Test behavioral intelligence
python -c "
from digital_forensic_surgeon.scanners.behavioral_intelligence import BehavioralIntelligence
intel = BehavioralIntelligence()
result = list(intel.scan_behavioral_patterns())
print(f'Behavioral Intelligence: Found {len(result)} behavioral patterns')
"
```

### 4. **Interactive Dashboard Test**
```bash
# Start the dashboard
python -c "
from digital_forensic_surgeon.dashboard.app import start_dashboard
start_dashboard(host='localhost', port=8000)
"

# Alternative: Direct module run
python -m digital_forensic_surgeon.dashboard.app
```

Then visit: **http://localhost:8000**

### 5. **Enhanced Reporting Test**
```python
# Test enhanced reporting
python -c "
from digital_forensic_surgeon.reporting.enhanced_reports import generate_enhanced_report
from digital_forensic_surgeon.core.models import EvidenceItem
from datetime import datetime

# Create test evidence
test_evidence = [
    EvidenceItem(
        id='test1',
        timestamp=datetime.now(),
        source='packet_analyzer',
        data_type='network_packet',
        description='Test packet capture',
        severity='medium',
        metadata={'protocol': 'tcp', 'volume': 1024}
    )
]

# Generate report
report = generate_enhanced_report(test_evidence, output_path='test_enhanced_report.html')
print(f'Enhanced Report: Generated report with {len(test_evidence)} evidence items')
"
```

### 6. **Integration Test - Full Beast Mode**
```python
# Test all components together
python -c "
import asyncio
from datetime import datetime
from digital_forensic_surgeon.scanners.packet_analyzer import PacketAnalyzer
from digital_forensic_surgeon.scanners.content_classifier import DataContentClassifier
from digital_forensic_surgeon.scanners.destination_intelligence import DestinationIntelligence
from digital_forensic_surgeon.scanners.application_monitor import ApplicationNetworkMonitor
from digital_forensic_surgeon.scanners.security_auditor import AccountSecurityAuditor
from digital_forensic_surgeon.scanners.behavioral_intelligence import BehavioralIntelligence
from digital_forensic_surgeon.reporting.enhanced_reports import generate_enhanced_report

print('🚀 Starting Beast Mode Integration Test...')

# Initialize all scanners
scanners = {
    'packet': PacketAnalyzer(),
    'content': DataContentClassifier(),
    'destination': DestinationIntelligence(),
    'application': ApplicationNetworkMonitor(),
    'security': AccountSecurityAuditor(),
    'behavioral': BehavioralIntelligence()
}

all_evidence = []

# Run quick scans
for name, scanner in scanners.items():
    print(f'🔍 Running {name} scanner...')
    try:
        if name == 'packet':
            results = list(scanner.scan_network_packets(duration=5))
        elif name == 'content':
            results = list(scanner.scan_content_classification(['C:\\Users\\shaik\\Documents']))
        elif name == 'destination':
            results = list(scanner.scan_destination_analysis(['google.com', 'github.com']))
        elif name == 'application':
            results = list(scanner.scan_application_network_activity())
        elif name == 'security':
            results = list(scanner.scan_account_security())
        elif name == 'behavioral':
            results = list(scanner.scan_behavioral_patterns())
        
        all_evidence.extend(results)
        print(f'✅ {name}: Found {len(results)} items')
    except Exception as e:
        print(f'❌ {name}: Error - {str(e)}')

print(f'📊 Total evidence collected: {len(all_evidence)}')

# Generate comprehensive report
if all_evidence:
    report = generate_enhanced_report(all_evidence, output_path='beast_mode_test_report.html')
    print('📋 Beast Mode Report Generated: beast_mode_test_report.html')
else:
    print('⚠️ No evidence collected for report generation')

print('🎉 Beast Mode Integration Test Complete!')
"
```

### 7. **CLI Commands Test**
```bash
# Test all CLI commands
forensic-surgeon --help
forensic-surgeon scan --help
forensic-surgeon scan filesystem --help
forensic-surgeon scan browser --help
forensic-surgeon scan network --help
forensic-surgeon scan credentials --help
forensic-surgeon scan osint --help
```

### 8. **Database & Configuration Test**
```python
# Test database operations
python -c "
from digital_forensic_surgeon.core.config import ForensicConfig
from digital_forensic_surgeon.db.manager import DatabaseManager

print('🗄️ Testing Database & Configuration...')

# Test configuration
config = ForensicConfig()
print(f'✅ Config loaded: DB path = {config.db_path}')

# Test database
try:
    db = DatabaseManager(config.db_path)
    services = db.get_all_services()
    print(f'✅ Database connected: {len(services)} services found')
except Exception as e:
    print(f'❌ Database error: {str(e)}')
"
```

### 9. **Performance & Stress Test**
```python
# Performance test
python -c "
import time
from digital_forensic_surgeon.scanners.packet_analyzer import PacketAnalyzer

print('⚡ Performance Test - Packet Analyzer...')
start_time = time.time()
analyzer = PacketAnalyzer()
results = list(analyzer.scan_network_packets(duration=10))
end_time = time.time()

print(f'📈 Performance: {len(results)} packets in {end_time - start_time:.2f} seconds')
print(f'🚀 Rate: {len(results) / (end_time - start_time):.2f} packets/second')
"
```

### 10. **Error Handling Test**
```python
# Test error handling
python -c "
print('🛡️ Testing Error Handling...')

test_cases = [
    ('packet_analyzer', lambda: list(PacketAnalyzer().scan_network_packets(duration=1))),
    ('content_classifier', lambda: list(DataContentClassifier().scan_content_classification(['nonexistent_path']))),
    ('destination_intel', lambda: list(DestinationIntelligence().scan_destination_analysis(['invalid_domain']))),
]

for name, test_func in test_cases:
    try:
        result = test_func()
        print(f'✅ {name}: Handled gracefully, result: {len(result)}')
    except Exception as e:
        print(f'⚠️ {name}: Expected error - {str(e)[:50]}...')
"
```

## 🎯 **Expected Results**

### ✅ **Success Indicators:**
- All scanners initialize without errors
- Packet analyzer captures network packets
- Content classifier processes files
- Destination intelligence analyzes domains
- Application monitor detects network activity
- Security auditor identifies issues
- Behavioral engine finds patterns
- Dashboard loads at http://localhost:8000
- Enhanced reports generate HTML files
- CLI commands respond with help text

### ⚠️ **Common Issues & Solutions:**
1. **Permission errors** - Run as administrator
2. **Network access** - Check firewall settings
3. **Missing dependencies** - Run `pip install -e .`
4. **Database errors** - Run `forensic-surgeon --setup-db`

## 📊 **Test Results Summary**

After running all commands, you should see:
- 🚀 Beast upgrade components working
- 📊 Evidence being collected
- 🎯 Dashboard displaying data
- 📋 Reports being generated
- ✅ All modules integrated properly

Run these commands systematically to verify your beast upgrade is fully operational!
