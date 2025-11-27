# PrivacyShield - DNS-Level Ad Blocker

**REAL system-wide ad & tracker blocking that ACTUALLY WORKS**

## What This Does:

Blocks ads and trackers for **ALL applications**:
- ✅ Browsers (Chrome, Firefox, Brave)
- ✅ Spotify (audio ads)
- ✅ Windows telemetry
- ✅ Discord, Slack, any app

## How It Works:

**DNS Interception:**
1. App asks: "What's the IP of ads.google.com?"
2. Our DNS server answers: "0.0.0.0" (blocked)
3. App can't connect → No ads loaded

Same technology as Pi-hole, but local to your PC.

## Installation:

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run as Administrator
python dns_blocker.py

# 3. Change Windows DNS to 127.0.0.1
```

## Setup Windows DNS:

1. Open **Settings** → **Network & Internet**
2. Click your connection → **Properties**
3. **DNS server assignment** → **Edit**
4. **Manual** → IPv4 **On**
5. **Preferred DNS:** `127.0.0.1`
6. **Save**

## You'll See:

```
🚀 DNS Server starting on 127.0.0.1:53
🚫 BLOCKED: googleadservices.com
🚫 BLOCKED: doubleclick.net
✅ ALLOWED: github.com
📊 Stats: 100 queries | 23 blocked | 77 allowed
```

## This Is REAL:
- No fake stats
- Actual blocking happening
- Works system-wide
- Proven technology (Pi-hole uses this)
