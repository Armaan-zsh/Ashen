// TrackerShield V3 Popup - Show decoded payloads + economic impact

async function calculatePrivacyScore() {
    const data = await chrome.storage.local.get(['todayBlocked', 'detectionLog', 'siteStats']);

    const todayBlocked = data.todayBlocked || 0;
    const detectionLog = data.detectionLog || [];
    const siteStats = data.siteStats || {};

    let score = 100;
    score -= Math.min(todayBlocked * 0.5, 40);

    const highRiskCount = detectionLog.filter(d =>
        d.trackers && d.trackers[0] && d.trackers[0].risk_score >= 8
    ).length;
    score -= Math.min(highRiskCount * 2, 30);

    const trackingSites = Object.keys(siteStats).length;
    score -= Math.min(trackingSites * 1, 20);

    score = Math.max(0, Math.min(100, score));

    let grade = 'F';
    if (score >= 90) grade = 'A+';
    else if (score >= 80) grade = 'A';
    else if (score >= 70) grade = 'B';
    else if (score >= 60) grade = 'C';
    else if (score >= 50) grade = 'D';

    return { score: Math.round(score), grade };
}

async function loadData() {
    const data = await chrome.storage.local.get([
        'totalBlocked',
        'todayBlocked',
        'detectionLog',
        'siteStats',
        'blockingEnabled',
        'totalEarned' // NEW
    ]);

    const todayBlocked = data.todayBlocked || 0;
    const totalBlocked = data.totalBlocked || 0;
    const detectionLog = data.detectionLog || [];
    const siteStats = data.siteStats || {};
    const blockingEnabled = data.blockingEnabled !== false;
    const totalEarned = data.totalEarned || 0; // NEW

    // Update stats
    document.getElementById('todayCount').textContent = todayBlocked;
    document.getElementById('totalCount').textContent = totalBlocked;

    // NEW: Economic counter
    document.getElementById('totalEarned').textContent = `₹${totalEarned.toFixed(2)}`;

    // Blocking toggle
    document.getElementById('blockingToggle').checked = blockingEnabled;

    // Privacy score
    const privacyScore = await calculatePrivacyScore();
    document.getElementById('privacyScore').textContent = privacyScore.score;
    document.getElementById('privacyGrade').textContent = privacyScore.grade;

    const scoreEl = document.getElementById('privacyScore');
    if (privacyScore.score >= 70) {
        scoreEl.style.color = '#00ff88';
    } else if (privacyScore.score >= 40) {
        scoreEl.style.color = '#ffaa00';
    } else {
        scoreEl.style.color = '#ff3b3b';
    }

    // Display detections with DECODED PAYLOADS
    const detectionList = document.getElementById('detectionList');

    if (detectionLog.length === 0) {
        detectionList.innerHTML = '<div class="empty">No trackers detected yet.<br>Browse the web to see protection!</div>';
        return;
    }

    detectionList.innerHTML = '';

    detectionLog.slice(0, 10).forEach(detection => {
        if (!detection.trackers || detection.trackers.length === 0) return;

        const tracker = detection.trackers[0];
        const timeAgo = getTimeAgo(detection.timestamp);

        const riskColor = tracker.risk_score >= 8 ? '#ff3b3b' :
            tracker.risk_score >= 6 ? '#ffaa00' : '#00ff88';

        // Format decoded data
        let decodedInfo = '';
        if (detection.decoded) {
            decodedInfo = `<div class="decoded-payload">
        📡 <strong>Decoded:</strong> ${detection.decoded.decoded || 'Tracking data sent'}
      </div>`;
        }

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
      ${decodedInfo}
      <div class="data-collected">
        <strong>Collecting:</strong> ${tracker.data_collected ? tracker.data_collected.slice(0, 3).join(', ') : 'User data'}
      </div>
      <div class="economic-impact">
        💰 They earned: ₹${(detection.value || 0.15).toFixed(2)}
      </div>
      <div class="detection-time">${timeAgo}</div>
    `;

        detectionList.appendChild(item);
    });

    // Top sites
    displayTopSites(siteStats);
}

function displayTopSites(siteStats) {
    const topSitesContainer = document.getElementById('topSites');
    if (!topSitesContainer) return;

    const sortedSites = Object.entries(siteStats)
        .sort((a, b) => b[1].count - a[1].count)
        .slice(0, 5);

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
      <div class="site-count">${stats.count} trackers | ₹${stats.earned.toFixed(2)} earned</div>
      <div class="site-companies">${companies}</div>
    `;
        topSitesContainer.appendChild(siteItem);
    });
}

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
            siteStats: {},
            totalEarned: 0
        });

        chrome.action.setBadgeText({ text: '' });
        loadData();
    }
});

// Share score
document.getElementById('shareBtn')?.addEventListener('click', async () => {
    const scoredata = await calculatePrivacyScore();
    const earnings = await chrome.storage.local.get(['totalEarned']);

    const text = `🛡️ TrackerShield Report

Privacy Score: ${scoredata.score}/100 (${scoredata.grade})
Trackers Blocked: ${document.getElementById('totalCount').textContent}
They Earned From Me: ₹${earnings.totalEarned?.toFixed(2) || '0.00'}

Taking back my privacy! Get TrackerShield`;

    navigator.clipboard.writeText(text);
    alert('✅ Copied! Share on social media to spread awareness.');
});

// Load data  
loadData();
setInterval(loadData, 2000);
