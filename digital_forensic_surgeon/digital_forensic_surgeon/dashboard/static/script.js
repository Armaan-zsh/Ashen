// Digital Forensic Surgeon Dashboard JavaScript
class ForensicDashboard {
    constructor() {
        this.scanners = [];
        this.evidence = [];
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadInitialData();
    }

    setupEventListeners() {
        document.querySelectorAll('.btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const action = e.target.dataset.action;
                if (action) {
                    this.handleAction(action);
                }
            });
        });
    }

    async handleAction(action) {
        const btn = document.querySelector(`[data-action="${action}"]`);
        btn.disabled = true;
        btn.textContent = 'Scanning...';

        try {
            const response = await fetch(`/api/${action}`, { method: 'POST' });
            const data = await response.json();
            
            if (data.success) {
                this.updateEvidence(data.evidence);
                this.showAlert(`${action} completed successfully!`, 'success');
            } else {
                this.showAlert(data.error || 'Scan failed', 'danger');
            }
        } catch (error) {
            this.showAlert(`Error: ${error.message}`, 'danger');
        } finally {
            btn.disabled = false;
            btn.textContent = action.charAt(0).toUpperCase() + action.slice(1);
        }
    }

    updateEvidence(newEvidence) {
        this.evidence = [...this.evidence, ...newEvidence];
        this.renderEvidence();
    }

    renderEvidence() {
        const container = document.querySelector('.evidence-list');
        container.innerHTML = this.evidence.map(item => `
            <div class="evidence-item">
                <h4>${item.source}</h4>
                <p>${item.content}</p>
                <small>Type: ${item.type} | ID: ${item.id}</small>
            </div>
        `).join('');
    }

    showAlert(message, type = 'info') {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type}`;
        alertDiv.textContent = message;
        
        document.querySelector('.container').insertBefore(
            alertDiv, 
            document.querySelector('.status-grid')
        );

        setTimeout(() => alertDiv.remove(), 5000);
    }

    async loadInitialData() {
        try {
            const response = await fetch('/api/status');
            const data = await response.json();
            this.updateStatus(data);
        } catch (error) {
            console.error('Failed to load initial data:', error);
        }
    }

    updateStatus(status) {
        Object.entries(status).forEach(([key, value]) => {
            const element = document.getElementById(`status-${key}`);
            if (element) {
                element.textContent = value;
            }
        });
    }
}

// Global functions for button onclick handlers
async function runScan(scanType, buttonElement) {
    // Get button element from parameter or find it
    const button = buttonElement || (typeof event !== 'undefined' ? event.target : null);
    if (!button) {
        console.error('Button element not found');
        return;
    }
    
    const originalText = button.textContent;
    
    button.disabled = true;
    button.textContent = 'Running...';
    
    try {
        const response = await fetch(`/api/run_scan/${scanType}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({})
        });
        
        const data = await response.json();
        
        if (response.ok && !data.error) {
            showAlert(`${scanType} scan completed successfully!`, 'success');
            // Refresh evidence list
            loadEvidence();
        } else {
            showAlert(data.error || `${scanType} scan failed`, 'danger');
        }
    } catch (error) {
        showAlert(`Error running ${scanType} scan: ${error.message}`, 'danger');
    } finally {
        button.disabled = false;
        button.textContent = originalText;
    }
}

async function toggleMonitoring(buttonElement) {
    // Get button element from parameter or find it
    const button = buttonElement || (typeof event !== 'undefined' ? event.target : null);
    if (!button) {
        console.error('Button element not found');
        return;
    }
    
    const originalText = button.textContent;
    const isStarting = originalText.includes('Start');
    
    button.disabled = true;
    button.textContent = isStarting ? 'Starting...' : 'Stopping...';
    
    try {
        const endpoint = isStarting ? '/api/start_monitoring' : '/api/stop_monitoring';
        const response = await fetch(endpoint, { method: 'POST' });
        const data = await response.json();
        
        if (response.ok) {
            button.textContent = isStarting ? 'Stop Monitoring' : 'Start Monitoring';
            showAlert(data.status || 'Monitoring status updated', 'success');
        } else {
            showAlert(data.error || 'Failed to toggle monitoring', 'danger');
        }
    } catch (error) {
        showAlert(`Error toggling monitoring: ${error.message}`, 'danger');
    } finally {
        button.disabled = false;
    }
}

function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert ${type}`;
    alertDiv.textContent = message;
    alertDiv.style.cssText = `
        background: ${type === 'success' ? '#d4edda' : type === 'danger' ? '#f8d7da' : '#d1ecf1'};
        color: ${type === 'success' ? '#155724' : type === 'danger' ? '#721c24' : '#0c5460'};
        padding: 12px;
        margin: 10px 0;
        border-radius: 4px;
        border: 1px solid ${type === 'success' ? '#c3e6cb' : type === 'danger' ? '#f5c6cb' : '#bee5eb'};
    `;
    
    // Try to find a container, otherwise use body
    const container = document.querySelector('.dashboard-grid') || 
                      document.querySelector('.header') || 
                      document.body;
    container.insertBefore(alertDiv, container.firstChild);
    
    setTimeout(() => alertDiv.remove(), 5000);
}

async function loadEvidence() {
    try {
        const response = await fetch('/api/evidence');
        const data = await response.json();
        
        const evidenceList = document.querySelector('.evidence-list');
        if (evidenceList && data.recent_evidence) {
            evidenceList.innerHTML = data.recent_evidence.map(item => `
                <div class="evidence-item" style="
                    background: rgba(255,255,255,0.1);
                    border-radius: 8px;
                    padding: 15px;
                    margin-bottom: 10px;
                    border-left: 4px solid #4CAF50;
                ">
                    <h4 style="margin: 0 0 10px 0; color: #4CAF50;">${item.source || 'Unknown'}</h4>
                    <p style="margin: 0 0 10px 0;">${item.content || 'No content'}</p>
                    <small style="opacity: 0.7;">Type: ${item.type || 'unknown'} | ID: ${item.id || 'N/A'}</small>
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('Failed to load evidence:', error);
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ForensicDashboard();
    loadEvidence();
});
