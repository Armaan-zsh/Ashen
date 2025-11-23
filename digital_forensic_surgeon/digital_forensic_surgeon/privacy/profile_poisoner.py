"""
Profile Poisoner
Generates fake browsing patterns to confuse trackers
"""

import random
from datetime import datetime, timedelta
from typing import List, Dict

class ProfilePoisoner:
    """Creates fake digital footprints to poison your tracking profile"""
    
    # Fake interests to confuse trackers
    FAKE_PERSONAS = {
        'luxury_buyer': {
            'searches': [
                'rolex watches for sale',
                'luxury yacht charter',
                'private jet rental',
                'bentley continental gt',
                'penthouse apartment mumbai',
                'diamond jewelry stores',
                'luxury vacation villas',
                'high-end fashion brands',
                'ferrari dealership near me',
                'luxury watches under 1 crore'
            ],
            'sites': [
                'luxuryrealestate.com',
                'sothebysrealty.com',
                'rolexretailer.com',
                'netjets.com',
                'christies.com'
            ]
        },
        'budget_traveler': {
            'searches': [
                'cheap flights to goa',
                'budget hotels delhi',
                'backpacking tips india',
                'hostel booking websites',
                'discount travel deals',
                'low cost airlines',
                'free things to do in mumbai',
                'student travel discounts',
                'camping gear sale',
                'hitchhiking safety tips'
            ],
            'sites': [
                'hostelworld.com',
                'skyscanner.com',
                'couchsurfing.com',
                'budgetyourtrip.com'
            ]
        },
        'health_fitness': {
            'searches': [
                'best gyms near me',
                'protein powder reviews',
                'marathon training plans',
                'yoga classes online',
                'meal prep ideas',
                'fitness tracker comparison',
                'crossfit workout routines',
                'nutrition calculator',
                'supplement store',
                'home workout equipment'
            ],
            'sites': [
                'myfitnesspal.com',
                'bodybuilding.com',
                'fitbit.com',
                'strava.com'
            ]
        },
        'business_investor': {
            'searches': [
                'stock market analysis',
                'cryptocurrency investment',
                'business loan rates',
                'startup funding options',
                'real estate investment',
                'mutual fund comparison',
                'tax planning strategies',
                'portfolio management',
                'forex trading tips',
                'gold price today'
            ],
            'sites': [
                'moneycontrol.com',
                'economictimes.com',
                'nseindia.com',
                'coinbase.com'
            ]
        },
        'gaming_tech': {
            'searches': [
                'gaming pc build 2024',
                'rtx 4090 price',
                'mechanical keyboard reviews',
                'gaming monitor 144hz',
                'steam summer sale',
                'gaming chair under 20000',
                'ps5 stock availability',
                'gaming headset wireless',
                'rgb mouse pad',
                'game release dates 2024'
            ],
            'sites': [
                'steam.com',
                'pcpartpicker.com',
                'reddit.com/r/gaming',
                'twitch.tv'
            ]
        }
    }
    
    def generate_poison_profile(self, num_personas: int = 3) -> Dict:
        """
        Generate a fake browsing profile
        
        Args:
            num_personas: How many fake interests to mix
        
        Returns:
            Dict with fake searches and sites
        """
        
        # Pick random personas
        selected_personas = random.sample(list(self.FAKE_PERSONAS.keys()), min(num_personas, len(self.FAKE_PERSONAS)))
        
        all_searches = []
        all_sites = []
        
        for persona in selected_personas:
            all_searches.extend(self.FAKE_PERSONAS[persona]['searches'])
            all_sites.extend(self.FAKE_PERSONAS[persona]['sites'])
        
        # Shuffle to mix them up
        random.shuffle(all_searches)
        random.shuffle(all_sites)
        
        return {
            'personas': selected_personas,
            'searches': all_searches[:30],  # 30 fake searches
            'sites': all_sites[:20],  # 20 fake sites
            'generated_at': datetime.now().isoformat()
        }
    
    def get_poison_instructions(self, profile: Dict) -> str:
        """Generate human-readable instructions for poisoning"""
        
        personas_str = ", ".join([p.replace('_', ' ').title() for p in profile['personas']])
        
        instructions = f"""
# 🎭 Profile Poisoning Instructions

## What This Does:
Trackers will think you're a **{personas_str}** instead of who you really are!

## How to Poison Your Profile:

### Option 1: Manual (Free)
1. Over the next week, search for these things on Google:
   - {profile['searches'][0]}
   - {profile['searches'][1]}
   - {profile['searches'][2]}
   - ... (and {len(profile['searches'])-3} more)

2. Visit these websites (just open and scroll):
   - {profile['sites'][0]}
   - {profile['sites'][1]}
   - ... (and {len(profile['sites'])-2} more)

### Option 2: Automated (Coming Soon)
Install our browser extension to automatically:
- Make fake searches in the background
- Visit decoy websites
- Generate fake clicks
- All without affecting your real browsing!

## Expected Results:
After 1-2 weeks, trackers will have a COMPLETELY WRONG profile of you:
- Wrong age range
- Wrong income level
- Wrong interests
- Wrong shopping behavior

**They'll waste money showing you irrelevant ads!** 😂

---

💡 **Pro Tip:** Run this monthly with different personas to keep them confused!
        """
        
        return instructions
    
    def generate_browser_script(self, profile: Dict) -> str:
        """Generate JavaScript to run in browser console"""
        
        searches = '", "'.join(profile['searches'][:10])
        
        script = f"""
// Profile Poisoner - Run this in your browser console
// This will open tabs with fake searches (CLOSE THEM AFTER!)

const fakeSearches = ["{searches}"];
const delay = 2000; // 2 seconds between searches

fakeSearches.forEach((search, index) => {{
    setTimeout(() => {{
        window.open(`https://www.google.com/search?q=${{encodeURIComponent(search)}}`, '_blank');
        console.log(`Opened: ${{search}}`);
    }}, delay * index);
}});

console.log('Profile poisoning started! Close tabs after Google logs them.');
        """
        
        return script
