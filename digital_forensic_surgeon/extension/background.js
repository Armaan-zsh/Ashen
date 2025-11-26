// TrackerShield Background Script V2
// NOW WITH BLOCKING + PER-SITE STATS

let signatures = [];
let todayBlocked = 0;
let totalBlocked = 0;
let detectionLog = [];
let siteStats = {}; // Per-site tracking stats
let blockingEnabled = true; // Global toggle

// Load signatures when extension starts
loadSignatures();
loadSettings();

// Load signatures from JSON
async function loadSignatures() {
  try {
    const url = chrome.runtime.getURL('signatures.json');
    const response = await fetch(url);
    const data = await response.json();
    signatures = data.signatures || [];
    console.log(`✅ Loaded ${signatures.length} signatures`);
  } catch (error) {
    console.error('Failed to load signatures:', error);
  }
}

// Load user settings
async function loadSettings() {
  chrome.storage.local.get(['blockingEnabled', 'siteStats'], (result) => {
    blockingEnabled = result.blockingEnabled !== false; // Default true
    siteStats = result.siteStats || {};
  });
}

// Extract domain from URL
function getDomain(url) {
  try {
    const urlObj = new URL(url);
    return urlObj.hostname;
  } catch {
    return 'unknown';
  }
}

// Match URL against signatures
function matchSignatures(url) {
  const matches = [];

  for (const sig of signatures) {
    if (!sig.patterns) continue;

    for (const pattern of sig.patterns) {
      if (!pattern.value) continue;

      // Simple contains match
      if (url.toLowerCase().includes(pattern.value.toLowerCase())) {
        matches.push({
          name: sig.name,
          company: sig.company,
          category: sig.category,
          risk_score: sig.risk_score,
          data_collected: getDataCollected(sig) // NEW: What data is collected
        });
        break;
      }
    }
  }

  return matches;
}

// Get what data this tracker collects (REAL data based on category)
function getDataCollected(sig) {
  const dataTypes = {
    'advertising': ['Page views', 'Clicks', 'Purchase intent', 'Shopping cart', 'Device info'],
    'analytics': ['Browsing behavior', 'Time on page', 'Scroll depth', 'Click patterns', 'Location'],
    'social': ['Social shares', 'Profile data', 'Friend lists', 'Interactions'],
    'tracking': ['User ID', 'Session data', 'Cross-site activity', 'Browsing history']
  };

  return dataTypes[sig.category] || ['User data', 'Activity tracking'];
}

// Listen to ALL web requests
chrome.webRequest.onBeforeRequest.addListener(
  (details) => {
    const url = details.url;
    const tabId = details.tabId;

    // Skip extension URLs
    if (url.startsWith('chrome-extension://')) return;

    // Check for trackers
    const matches = matchSignatures(url);

    if (matches.length > 0) {
      // Get the current tab's URL to track per-site stats
      chrome.tabs.get(tabId, (tab) => {
        if (chrome.runtime.lastError || !tab) return;

        const siteDomain = getDomain(tab.url);

        // Update per-site stats
        if (!siteStats[siteDomain]) {
          siteStats[siteDomain] = {
            count: 0,
            trackers: {}
          };
        }

        siteStats[siteDomain].count++;

        // Track which companies track this site
        for (const match of matches) {
          if (!siteStats[siteDomain].trackers[match.company]) {
            siteStats[siteDomain].trackers[match.company] = 0;
          }
          siteStats[siteDomain].trackers[match.company]++;
        }

        // Save site stats
        chrome.storage.local.set({ siteStats });
      });

      // Update detection stats
      todayBlocked++;
      totalBlocked++;

      const detection = {
        timestamp: Date.now(),
        url: url,
        trackers: matches,
        tabId: tabId
      };

      detectionLog.unshift(detection);
      if (detectionLog.length > 100) detectionLog.pop();

      // Save to storage
      chrome.storage.local.set({
        totalBlocked,
        todayBlocked,
        detectionLog
      });

      // Update badge
      chrome.action.setBadgeText({
        text: todayBlocked.toString()
      });
      chrome.action.setBadgeBackgroundColor({
        // Color based on risk
        color: matches[0].risk_score >= 8 ? '#ff0000' : '#ff3b3b'
      });

      console.log('🚫 Detected:', matches[0].company, 'Risk:', matches[0].risk_score);
    }
  },
  { urls: ['<all_urls>'] }
);

// BLOCKING: Actually block tracker requests
chrome.webRequest.onBeforeRequest.addListener(
  (details) => {
    const url = details.url;

    // Skip extension URLs
    if (url.startsWith('chrome-extension://')) return;

    // Check if blocking enabled
    if (!blockingEnabled) return;

    // Check for trackers
    const matches = matchSignatures(url);

    if (matches.length > 0 && matches[0].risk_score >= 7) {
      // Block high-risk trackers (7+)
      console.log('⛔ BLOCKED:', matches[0].company, url.substring(0, 50));
      return { cancel: true };
    }
  },
  { urls: ['<all_urls>'] },
  ['blocking'] // Enable blocking
);

// Load saved data on startup
chrome.storage.local.get(['totalBlocked', 'todayBlocked', 'detectionLog', 'blockingEnabled'], (result) => {
  totalBlocked = result.totalBlocked || 0;
  todayBlocked = result.todayBlocked || 0;
  detectionLog = result.detectionLog || [];
  blockingEnabled = result.blockingEnabled !== false;

  if (todayBlocked > 0) {
    chrome.action.setBadgeText({ text: todayBlocked.toString() });
    chrome.action.setBadgeBackgroundColor({ color: '#ff3b3b' });
  }
});

// Reset daily count at midnight
function resetDaily() {
  const now = new Date();
  const tomorrow = new Date(now);
  tomorrow.setDate(tomorrow.getDate() + 1);
  tomorrow.setHours(0, 0, 0, 0);

  setTimeout(() => {
    todayBlocked = 0;
    chrome.storage.local.set({ todayBlocked: 0 });
    chrome.action.setBadgeText({ text: '' });
    resetDaily();
  }, tomorrow - now);
}

resetDaily();
