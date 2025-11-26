// TrackerShield Background Script
// Monitors web requests and detects trackers in real-time

let signatures = [];
let todayBlocked = 0;
let totalBlocked = 0;
let detectionLog = [];

// Load signatures on install/startup
chrome.runtime.onInstalled.addListener(async () => {
  console.log('TrackerShield installed!');
  await loadSignatures();

  // Initialize storage
  chrome.storage.local.set({
    totalBlocked: 0,
    todayBlocked: 0,
    detectionLog: []
  });
});

// Load on startup too
loadSignatures();

// Load signatures from JSON
async function loadSignatures() {
  try {
    const url = chrome.runtime.getURL('signatures.json');
    console.log('Loading signatures from:', url);

    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    signatures = data.signatures || [];

    console.log(`✅ Loaded ${signatures.length} signatures`);
    console.log('Sample signature:', signatures[0]);

    return true;
  } catch (error) {
    console.error('❌ Failed to load signatures:', error);
    return false;
    const url = details.url;

    // Skip extension's own requests
    if (url.startsWith('chrome-extension://')) return;

    // Match against signatures
    const matches = matchSignatures(url);

    if (matches.length > 0) {
      // Tracker detected!
      todayBlocked++;
      totalBlocked++;

      // Log detection
      const detection = {
        timestamp: Date.now(),
        url: url,
        trackers: matches,
        tabId: details.tabId
      };

      detectionLog.unshift(detection);
      if (detectionLog.length > 100) {
        detectionLog.pop(); // Keep last 100
      }

      // Update storage
      chrome.storage.local.set({
        totalBlocked,
        todayBlocked,
        detectionLog
      });

      // Update badge
      updateBadge();

      console.log('Tracker detected:', matches[0].company);
    }
  },
  { urls: ['<all_urls>'] }
);

  // Update badge with count
  function updateBadge() {
    chrome.action.setBadgeText({
      text: todayBlocked > 0 ? todayBlocked.toString() : ''
    });

    chrome.action.setBadgeBackgroundColor({
      color: '#ff3b3b'
    });
  }

  // Reset daily count at midnight
  function resetDailyCount() {
    const now = new Date();
    const tomorrow = new Date(now);
    tomorrow.setDate(tomorrow.getDate() + 1);
    tomorrow.setHours(0, 0, 0, 0);

    const msUntilMidnight = tomorrow - now;

    setTimeout(() => {
      todayBlocked = 0;
      updateBadge();
      chrome.storage.local.set({ todayBlocked: 0 });
      resetDailyCount(); // Schedule next reset
    }, msUntilMidnight);
  }

  // Load saved data on startup
  chrome.storage.local.get(['totalBlocked', 'todayBlocked', 'detectionLog'], (result) => {
    totalBlocked = result.totalBlocked || 0;
    todayBlocked = result.todayBlocked || 0;
    detectionLog = result.detectionLog || [];
    updateBadge();
    resetDailyCount();
  });

  // Initialize
  loadSignatures();
