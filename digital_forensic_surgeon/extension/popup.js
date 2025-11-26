// TrackerShield Popup Script
// Displays detection stats and recent trackers

// Load and display data
async function loadData() {
    const data = await chrome.storage.local.get(['totalBlocked', 'todayBlocked', 'detectionLog']);

    // Update stats
    document.getElementById('todayCount').textContent = data.todayBlocked || 0;
    document.getElementById('totalCount').textContent = data.totalBlocked || 0;

    // Display recent detections
    const detectionList = document.getElementById('detectionList');
    const log = data.detectionLog || [];

    if (log.length === 0) {
        detectionList.innerHTML = '<div class="empty">No trackers detected yet.<br>Browse the web to see detections!</div>';
        return;
    }

    detectionList.innerHTML = '';

    // Show last 10 detections
    log.slice(0, 10).forEach(detection => {
        const trackerInfo = detection.trackers[0]; // First tracker
        const timeAgo = getTimeAgo(detection.timestamp);

        const item = document.createElement('div');
        item.className = 'detection-item';
        item.innerHTML = `
      <div class="detection-company">${trackerInfo.company}</div>
      <div class="detection-name">${trackerInfo.name}</div>
      <div class="detection-time">${timeAgo}</div>
    `;

        detectionList.appendChild(item);
    });
}

// Format time ago
function getTimeAgo(timestamp) {
    const seconds = Math.floor((Date.now() - timestamp) / 1000);

    if (seconds < 60) return 'Just now';
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
    return `${Math.floor(seconds / 86400)}d ago`;
}

// Clear history
document.getElementById('clearBtn').addEventListener('click', () => {
    if (confirm('Clear all detection history?')) {
        chrome.storage.local.set({
            totalBlocked: 0,
            todayBlocked: 0,
            detectionLog: []
        });

        // Reset badge
        chrome.action.setBadgeText({ text: '' });

        // Reload popup
        loadData();
    }
});

// Load data when popup opens
loadData();

// Update every 2 seconds while popup is open
setInterval(loadData, 2000);
