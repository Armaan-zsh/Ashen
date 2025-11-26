// TrackerShield V3 Popup - Simple version

async function loadData() {
    const data = await chrome.storage.local.get([
        'totalBlocked',
        'todayBlocked',
        'detectionLog'
    ]);

    const todayBlocked = data.todayBlocked || 0;
    const totalBlocked = data.totalBlocked || 0;
    const detectionLog = data.detectionLog || [];

    // Update stats
    document.getElementById('todayCount').textContent = todayBlocked;
    document.getElementById('totalCount').textContent = totalBlocked;

    // Display detections
    const detectionList = document.getElementById('detectionList');

    if (detectionLog.length === 0) {
        detectionList.innerHTML = '<div class="empty">No trackers detected yet.<br>Browse to see protection!</div>';
        return;
    }

    detectionList.innerHTML = '';

    detectionLog.slice(0, 10).forEach(detection => {
        if (!detection.trackers || detection.trackers.length === 0) return;

        const tracker = detection.trackers[0];
        const timeAgo = getTimeAgo(detection.timestamp);

        const item = document.createElement('div');
        item.className = 'detection-item';
        item.innerHTML = `
      <div class="detection-company">${tracker.company}</div>
      <div class="detection-name">${tracker.name}</div>
      <div class="detection-time">${timeAgo}</div>
    `;

        detectionList.appendChild(item);
    });
}

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

        chrome.action.setBadgeText({ text: '' });
        loadData();
    }
});

// Load data
loadData();
setInterval(loadData, 2000);
