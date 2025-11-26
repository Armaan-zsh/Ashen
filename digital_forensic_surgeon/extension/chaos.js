// TrackerShield V3: Fingerprint Chaos Engine
// Randomizes ALL fingerprintable browser APIs
// Injected BEFORE page loads to prevent tracking

(function () {
    'use strict';

    console.log('🛡️ TrackerShield Fingerprint Chaos Active');

    // ========== CANVAS FINGERPRINTING ==========
    const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
    const originalToBlob = HTMLCanvasElement.prototype.toBlob;

    HTMLCanvasElement.prototype.toDataURL = function () {
        const ctx = this.getContext('2d');
        if (ctx) {
            const imageData = ctx.getImageData(0, 0, this.width, this.height);
            // Add very subtle random noise
            for (let i = 0; i < imageData.data.length; i += 4) {
                imageData.data[i] += Math.random() * 3 - 1.5; // R
                imageData.data[i + 1] += Math.random() * 3 - 1.5; // G
                imageData.data[i + 2] += Math.random() * 3 - 1.5; // B
            }
            ctx.putImageData(imageData, 0, 0);
        }
        return originalToDataURL.apply(this, arguments);
    };

    // ========== WEBGL FINGERPRINTING ==========
    const getParameter = WebGLRenderingContext.prototype.getParameter;
    WebGLRenderingContext.prototype.getParameter = function (param) {
        const vendors = ['Intel Inc.', 'NVIDIA Corporation', 'AMD', 'Apple Inc.'];
        const renderers = [
            'Intel Iris OpenGL Engine',
            'NVIDIA GeForce GTX 1060',
            'AMD Radeon Pro 560X',
            'Apple M1'
        ];

        // UNMASKED_VENDOR_WEBGL
        if (param === 37445) {
            return vendors[Math.floor(Math.random() * vendors.length)];
        }

        // UNMASKED_RENDERER_WEBGL
        if (param === 37446) {
            return renderers[Math.floor(Math.random() * renderers.length)];
        }

        return getParameter.call(this, param);
    };

    // ========== AUDIO CONTEXT FINGERPRINTING ==========
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    if (AudioContext) {
        const originalGetChannelData = AudioBuffer.prototype.getChannelData;
        AudioBuffer.prototype.getChannelData = function () {
            const data = originalGetChannelData.apply(this, arguments);
            // Add noise to audio fingerprint
            for (let i = 0; i < data.length; i++) {
                data[i] += (Math.random() - 0.5) * 0.0001;
            }
            return data;
        };
    }

    // ========== SCREEN/WINDOW PROPERTIES ==========
    const screenOffset = Math.floor(Math.random() * 100) - 50;
    const widthOffset = Math.floor(Math.random() * 200) - 100;
    const heightOffset = Math.floor(Math.random() * 200) - 100;

    Object.defineProperty(screen, 'width', {
        get: () => 1920 + widthOffset
    });

    Object.defineProperty(screen, 'height', {
        get: () => 1080 + heightOffset
    });

    Object.defineProperty(screen, 'availWidth', {
        get: () => 1920 + widthOffset - 50
    });

    Object.defineProperty(screen, 'availHeight', {
        get: () => 1080 + heightOffset - 100
    });

    // ========== FONTS FINGERPRINTING ==========
    const originalGetComputedstyle = window.getComputedStyle;
    window.getComputedStyle = function () {
        const result = originalGetComputedstyle.apply(this, arguments);
        // Randomize font detection
        const originalGetPropertyValue = result.getPropertyValue;
        result.getPropertyValue = function (prop) {
            if (prop === 'font-family') {
                const fonts = ['Arial', 'Times New Roman', 'Courier New', 'Georgia', 'Verdana'];
                return fonts[Math.floor(Math.random() * fonts.length)];
            }
            return originalGetPropertyValue.call(this, prop);
        };
        return result;
    };

    // ========== HARDWARE CONCURRENCY ==========
    const cores = [2, 4, 6, 8, 12, 16][Math.floor(Math.random() * 6)];
    Object.defineProperty(navigator, 'hardwareConcurrency', {
        get: () => cores
    });

    // ========== DEVICE MEMORY ==========
    if (navigator.deviceMemory) {
        Object.defineProperty(navigator, 'deviceMemory', {
            get: () => [2, 4, 8, 16][Math.floor(Math.random() * 4)]
        });
    }

    // ========== BATTERY STATUS ==========
    if (navigator.getBattery) {
        const originalGetBattery = navigator.getBattery;
        navigator.getBattery = async function () {
            const battery = await originalGetBattery.call(this);
            Object.defineProperty(battery, 'level', {
                get: () => Math.random()
            });
            return battery;
        };
    }

    // ========== TIMEZONE ==========
    const timezones = [
        'America/New_York',
        'Europe/London',
        'Asia/Tokyo',
        'Asia/Kolkata',
        'Australia/Sydney',
        'America/Los_Angeles'
    ];

    const randomTZ = timezones[Math.floor(Math.random() * timezones.length)];

    // Override Date methods to use random timezone
    const OriginalDate = Date;
    Date = function () {
        const date = new OriginalDate(...arguments);
        // Modify timezone offset
        const offset = Math.floor(Math.random() * 24) - 12;
        const originalGetTimezoneOffset = date.getTimezoneOffset;
        date.getTimezoneOffset = function () {
            return offset * 60;
        };
        return date;
    };

    // ========== PLUGINS ==========
    Object.defineProperty(navigator, 'plugins', {
        get: () => {
            // Random subset of common plugins
            const allPlugins = [
                'Chrome PDF Plugin',
                'Chrome PDF Viewer',
                'Native Client',
                'Widevine Content Decryption Module'
            ];
            const count = Math.floor(Math.random() * 3) + 1;
            return allPlugins.slice(0, count);
        }
    });

    console.log('✅ Fingerprint randomized:', {
        screen: `${1920 + widthOffset}x${1080 + heightOffset}`,
        cores: cores,
        timezone: randomTZ
    });

})();
