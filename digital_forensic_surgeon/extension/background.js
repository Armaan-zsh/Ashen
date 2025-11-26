// TrackerShield Background Script
// Monitors web requests and detects trackers

let signatures = [];
let todayBlocked = 0;
let totalBlocked = 0;
let detectionLog = [];

// Load signatures when extension starts
loadSignatures();

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
          risk_score: sig.risk_score
        });
        break;
      }
    }
  }

  return matches;
}

// Listen to ALL web requests
chrome.webRequest.onBeforeRequest.addListener(
  (details) => {
    const url = details.url;

    // Skip extension URLs
    if (url.startsWith('chrome-extension://')) return;

    // Check for trackers
    const matches = matchSignatures(url);

    if (matches.length > 0) {
      todayBlocked++;
      totalBlocked++;

      const detection = {
        timestamp: Date.now(),
        url: url,
        trackers: matches
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
        color: '#ff3b3b'
      });

      console.log('🚫 Blocked:', matches[0].company, url.substring(0, 50));
    }
  },
  { urls: ['<all_urls>'] }
);

// Load saved data on startup
chrome.storage.local.get(['totalBlocked', 'todayBlocked', 'detectionLog'], (result) => {
  totalBlocked = result.totalBlocked || 0;
  todayBlocked = result.todayBlocked || 0;
  detectionLog = result.detectionLog || [];

  if (todayBlocked > 0) {
    chrome.action.setBadgeText({ text: todayBlocked.toString() });
    chrome.action.setBadgeBackgroundColor({ color: '#ff3b3b' });
  }
});
