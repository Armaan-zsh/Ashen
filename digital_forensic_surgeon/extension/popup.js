// TrackerShield Popup V2 - Modern UI with REAL data
// Shows blocking, data collection, per-site stats, privacy score

// Calculate REAL privacy score from actual data
async function calculatePrivacyScore() {
    const data = await chrome.storage.local.get(['todayBlocked', 'totalBlocked', 'detectionLog', 'siteStats']);

    const todayBlocked = data.todayBlocked || 0;
    const detectionLog = data.detectionLog || [];
    const siteStats = data.siteStats || {};

    // Base score starts at 100
    let score = 100;

    // Deduct based on trackers today (more trackers = worse privacy)
    score -= Math.min(todayBlocked * 0.5, 40); // Max -40 points

    // Deduct based on high-risk trackers
    const highRiskCount = detectionLog.filter(d =>
        d.trackers && d.trackers[0] && d.trackers[0].risk_score >= 8
    ).length;
    score -= Math.min(highRiskCount * 2, 30); // Max -30 points

    // Deduct based on number of sites tracking you
    const trackingSites = Object.keys(siteStats).length;
    score -= Math.min(trackingSites * 1, 20); // Max -20 points

    // Ensure score is 0-100
    score = Math.max(0, Math.min(100, score));

    // Grade
    let grade = 'F';
    if (score >= 90) grade = 'A+';
    else if (score >= 80) grade = 'A';
    else if (score >= 70) grade = 'B';
    else if (score >= 60) grade = 'C';
    else if (score >= 50) grade = 'D';

    return { score: Math.round(score), grade };
}

// Load and display all data
async function loadData() {
    const data = await chrome.storage.local.get([
        'totalBlocked',
        'todayBlocked',
        'detectionLog',
        'siteStats',
        'blockingEnabled'
    ]);

    const todayBlocked = data.todayBlocked || 0;
    const totalBlocked = data.totalBlocked || 0;
    const detectionLog = data.detectionLog || [];
    const siteStats = data.siteStats || {};
    const blockingEnabled = data.blockingEnabled !== false;

    // Update stats
    document.getElementById('todayCount').textContent = todayBlocked;
    document.getElementById('totalCount').textContent = totalBlocked;

    // Update blocking toggle
    document.getElementById('blockingToggle').checked = blockingEnabled;

    // Calculate and show privacy score
    const privacyScore = await calculatePrivacyScore();
    document.getElementById('privacyScore').textContent = privacyScore.score;
    document.getElementById('privacyGrade').textContent = privacyScore.grade;

    // Color code the score
    const scoreEl = document.getElementById('privacyScore');
    if (privacyScore.score >= 70) {
        scoreEl.style.color = '#00ff88';
    } else if (privacyScore.score >= 40) {
        scoreEl.style.color = '#ffaa00';
    } else {
        scoreEl.style.color = '#ff3b3b';
    }

    // Display recent detections with data collected info
    const detectionList = document.getElementById('detectionList');

    if (detectionLog.length === 0) {
        detectionList.innerHTML = '<div class="empty">No trackers detected yet.<br>Browse the web to see protection!</div>';
        return;
    }

    detectionList.innerHTML = '';

    // Show last 10 detections
    detectionLog.slice(0, 10).forEach(detection => {
        if (!detection.trackers || detection.trackers.length === 0) return;

        const tracker = detection.trackers[0];
        const timeAgo = getTimeAgo(detection.timestamp);

        // Risk color
        const riskColor = tracker.risk_score >= 8 ? '#ff3b3b' :
            tracker.risk_score >= 6 ? '#ffaa00' : '#00ff88';

        const item = document.createElement('div');
        item.className = 'detection-item';
        item.style.borderLeftColor = riskColor;
        item.innerHTML = `
      <div class="detection-header">
        <span class="detection-company">${tracker.company}</span>
        <span class="risk-badge" style="background: ${riskColor}">
          ${tracker.risk_score}/10
        </span>
      </div>
      <div class="detection-name">${tracker.name}</div>
      <div class="data-collected">
        <strong>Collecting:</strong> ${tracker.data_collected ? tracker.data_collected.slice(0, 3).join(', ') : 'User data'}
      </div>
      <div class="detection-time">${timeAgo}</div>
    `;

        detectionList.appendChild(item);
    });

    // Show top tracking sites
    displayTopSites(siteStats);
}

// Display top sites that track you most
function displayTopSites(siteStats) {
    const topSitesContainer = document.getElementById('topSites');
    if (!topSitesContainer) return;

    // Sort sites by tracker count
    const sortedSites = Object.entries(siteStats)
        .sort((a, b) => b[1].count - a[1].count)
        .slice(0, 5); // Top 5

    if (sortedSites.length === 0) {
        topSitesContainer.innerHTML = '<div class="empty">No site data yet</div>';
        return;
    }

    topSitesContainer.innerHTML = '<h4>🔴 Top Tracking Sites</h4>';

    sortedSites.forEach(([site, stats]) => {
        const companies = Object.keys(stats.trackers).join(', ');
        const siteItem = document.createElement('div');
        siteItem.className = 'site-stat';
        siteItem.innerHTML = `
      <div class="site-name">${site}</div>
      <div class="site-count">${stats.count} trackers</div>
      <div class="site-companies">${companies}</div>
    `;
        topSitesContainer.appendChild(siteItem);
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

// Blocking toggle
document.getElementById('blockingToggle').addEventListener('change', (e) => {
    const enabled = e.target.checked;
    chrome.storage.local.set({ blockingEnabled: enabled });

    const status = document.getElementById('blockingStatus');
    status.textContent = enabled ? 'Active' : 'Paused';
    status.style.color = enabled ? '#00ff88' : '#ff3b3b';
});

// Clear history
document.getElementById('clearBtn').addEventListener('click', () => {
    if (confirm('Clear all detection history?')) {
        chrome.storage.local.set({
            totalBlocked: 0,
            todayBlocked: 0,
            detectionLog: [],
            siteStats: {}
        });

        chrome.action.setBadgeText({ text: '' });
        loadData();
    }
});

// Share privacy score
document.getElementById('shareBtn')?.addEventListener('click', async () => {
    const score = await calculatePrivacyScore();
    const text = `🛡️ My Privacy Score: ${score.score}/100 (${score.grade})

I blocked ${document.getElementById('totalCount').textContent} trackers with TrackerShield!

Protect your privacy: [Your Extension Link]`;

    navigator.clipboard.writeText(text);
    alert('✅ Copied to clipboard! Share on social media.');
});

// Load data when popup opens
loadData();

// Update every 2 seconds while popup is open
setInterval(loadData, 2000);
