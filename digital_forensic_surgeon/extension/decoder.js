// TrackerShield V3: Payload Decoder
// Decodes what trackers are ACTUALLY sending

const PayloadDecoder = {

    // Decode Facebook Pixel
    decodeFacebookPixel(url) {
        try {
            const urlObj = new URL(url);
            const params = urlObj.searchParams;

            return {
                company: 'Facebook/Meta',
                event: params.get('ev') || 'PageView',
                value: params.get('vl') || '0',
                currency: params.get('cu') || 'USD',
                userData: {
                    em: params.get('ud[em]'), // Email (hashed)
                    ph: params.get('ud[ph]'), // Phone (hashed)
                    fn: params.get('ud[fn]'), // First name (hashed)
                    ln: params.get('ud[ln]'), // Last name (hashed)
                    ct: params.get('ud[ct]'), // City
                    st: params.get('ud[st]'), // State
                    zp: params.get('ud[zp]'), // Zip
                    country: params.get('ud[country]')
                },
                decoded: `Tracking: ${params.get('ev') || 'PageView'} event with value $${params.get('vl') || '0'}`
            };
        } catch (e) {
            return null;
        }
    },

    // Decode Google Analytics
    decodeGoogleAnalytics(url) {
        try {
            const urlObj = new URL(url);
            const params = urlObj.searchParams;

            return {
                company: 'Google',
                clientId: params.get('cid'),
                documentLocation: params.get('dl'),
                documentTitle: params.get('dt'),
                screenResolution: params.get('sr'),
                viewportSize: params.get('vp'),
                language: params.get('ul'),
                encoding: params.get('de'),
                eventCategory: params.get('ec'),
                eventAction: params.get('ea'),
                decoded: `Tracking: Page "${params.get('dt')}" | Screen: ${params.get('sr')} | Language: ${params.get('ul')}`
            };
        } catch (e) {
            return null;
        }
    },

    // Decode Amazon OneTag
    decodeAmazonTracking(url) {
        if (!url.includes('amazon-adsystem.com')) return null;

        return {
            company: 'Amazon',
            decoded: 'Tracking browsing behavior and purchase intent'
        };
    },

    // Decode TikTok Pixel
    decodeTikTokPixel(url) {
        if (!url.includes('analytics.tiktok.com')) return null;

        return {
            company: 'TikTok/ByteDance',
            decoded: 'Tracking user engagement and conversions'
        };
    },

    // Decode Google Doubleclick
    decodeDoubleclick(url) {
        if (!url.includes('doubleclick.net')) return null;

        return {
            company: 'Google (Doubleclick)',
            decoded: 'Ad tracking and targeting data collection'
        };
    },

    // Master decoder
    decode(url) {
        // Try each decoder
        if (url.includes('facebook.com/tr')) {
            return this.decodeFacebookPixel(url);
        }

        if (url.includes('google-analytics.com') || url.includes('/collect')) {
            return this.decodeGoogleAnalytics(url);
        }

        if (url.includes('amazon-adsystem.com')) {
            return this.decodeAmazonTracking(url);
        }

        if (url.includes('analytics.tiktok.com')) {
            return this.decodeTikTokPixel(url);
        }

        if (url.includes('doubleclick.net')) {
            return this.decodeDoubleclick(url);
        }

        return null;
    },

    // Calculate economic value
    calculateValue(event) {
        const VALUES = {
            'PageView': 0.15,
            'ViewContent': 0.25,
            'AddToCart': 1.50,
            'InitiateCheckout': 3.00,
            'Purchase': 5.00,
            'Lead': 10.00,
            'CompleteRegistration': 8.00
        };

        return VALUES[event] || 0.10;
    }
};

// Export for background script
if (typeof module !== 'undefined') {
    module.exports = PayloadDecoder;
}
