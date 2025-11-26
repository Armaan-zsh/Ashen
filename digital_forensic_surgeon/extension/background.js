// TrackerShield V3 Background Script
// WITH: Payload decoding + Economic calculator

let signatures = [];
let todayBlocked = 0;
let totalBlocked = 0;
let detectionLog = [];
let siteStats = {};
let blockingEnabled = true;
let totalEarned = 0; // NEW: Economic tracker

// Load signatures and decoder
loadSignatures();
loadSettings();

// Import decoder (for module)
importScripts('decoder.js');

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

async function loadSettings() {
  chrome.storage.local.get(['blockingEnabled', 'siteStats', 'totalEarned'], (result) => {
    blockingEnabled = result.blockingEnabled !== false;
    siteStats = result.siteStats || {};
    totalEarned = result.totalEarned || 0;
  });
}

function getDomain(url) {
  try {
    const urlObj = new URL(url);
    return urlObj.hostname;
  } catch {
    return 'unknown';
  }
}

function matchSignatures(url) {
  const matches = [];

  for (const sig of signatures) {
    if (!sig.patterns) continue;

    for (const pattern of sig.patterns) {
      if (!pattern.value) continue;

      if (url.toLowerCase().includes(pattern.value.toLowerCase())) {
        matches.push({
          name: sig.name,
          company: sig.company,
          category: sig.category,
          risk_score: sig.risk_score,
          data_collected: getDataCollected(sig)
        });
        break;
      }
    }
  }

  return matches;
}

function getDataCollected(sig) {
  const dataTypes = {
    'advertising': ['Page views', 'Clicks', 'Purchase intent', 'Shopping cart', 'Device info'],
    'analytics': ['Browsing behavior', 'Time on page', 'Scroll depth', 'Click patterns', 'Location'],
    'social': ['Social shares', 'Profile data', 'Friend lists', 'Interactions'],
    'tracking': ['User ID', 'Session data', 'Cross-site activity', 'Browsing history']
  };

  return dataTypes[sig.category] || ['User data', 'Activity tracking'];
}

// Listen to web requests
chrome.webRequest.onBeforeRequest.addListener(
  (details) => {
    const url = details.url;
    const tabId = details.tabId;

    if (url.startsWith('chrome-extension://')) return;

    // NEW: Decode payload
    const decoded = PayloadDecoder.decode(url);

    // Match signatures
    const matches = matchSignatures(url);

    if (matches.length > 0) {
      // Calculate economic value
      const eventValue = decoded ?
        PayloadDecoder.calculateValue(decoded.event) :
        0.15; // Default pageview value

      totalEarned += eventValue;

      // Get current tab
      chrome.tabs.get(tabId, (tab) => {
        if (chrome.runtime.lastError || !tab) return;

        const siteDomain = getDomain(tab.url);

        // Update site stats
        if (!siteStats[siteDomain]) {
          siteStats[siteDomain] = {
            count: 0,
            earned: 0,
            trackers: {}
          };
        }

        siteStats[siteDomain].count++;
        siteStats[siteDomain].earned += eventValue;

        for (const match of matches) {
          if (!siteStats[siteDomain].trackers[match.company]) {
            siteStats[siteDomain].trackers[match.company] = 0;
          }
          siteStats[siteDomain].trackers[match.company]++;
        }

        chrome.storage.local.set({ siteStats });
      });

      // Update counters
      todayBlocked++;
      totalBlocked++;

      const detection = {
        timestamp: Date.now(),
        url: url,
        trackers: matches,
        decoded: decoded,
        value: eventValue,
        tabId: tabId
      };

      detectionLog.unshift(detection);
      if (detectionLog.length > 100) detectionLog.pop();

      // Save
      chrome.storage.local.set({
        totalBlocked,
        todayBlocked,
        detectionLog,
        totalEarned
      });

      // Update badge
      chrome.action.setBadgeText({
        text: todayBlocked.toString()
      });

      const badgeColor = matches[0].risk_score >= 8 ? '#ff0000' : '#ff3b3b';
      chrome.action.setBadgeBackgroundColor({ color: badgeColor });

      console.log('🛡️ Detected:', matches[0].company,
        '| Value: ₹' + eventValue.toFixed(2),
        decoded ? '| Decoded: ' + decoded.decoded : '');
    }
  },
  { urls: ['<all_urls>'] }
);

// BLOCKING (if enabled)
chrome.webRequest.onBeforeRequest.addListener(
  (details) => {
    if (!blockingEnabled) return;
    if (details.url.startsWith('chrome-extension://')) return;

    const matches = matchSignatures(details.url);

    if (matches.length > 0 && matches[0].risk_score >= 7) {
      console.log('⛔ BLOCKED:', matches[0].company);
      return { cancel: true };
    }
  },
  { urls: ['<all_urls>'] },
  ['blocking']
);

// Load saved data
chrome.storage.local.get([
  'totalBlocked',
  'todayBlocked',
  'detectionLog',
  'blockingEnabled',
  'totalEarned'
], (result) => {
  totalBlocked = result.totalBlocked || 0;
  todayBlocked = result.todayBlocked || 0;
  detectionLog = result.detectionLog || [];
  blockingEnabled = result.blockingEnabled !== false;
  totalEarned = result.totalEarned || 0;

  if (todayBlocked > 0) {
    chrome.action.setBadgeText({ text: todayBlocked.toString() });
    chrome.action.setBadgeBackgroundColor({ color: '#ff3b3b' });
  }
});

// Reset daily at midnight
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
