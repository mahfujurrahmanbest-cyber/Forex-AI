"""News Gate Service - Blocks trades near high-impact events."""
from datetime import datetime, timedelta
from typing import Dict, Any, List
import random


class NewsGateService:
    """
    News Gate Service.
    
    Checks ForexFactory calendar and blocks trades:
    - Red news < 60 minutes: BLOCKED
    - Red news < 120 minutes: CAUTION
    - No red news: CLEAR
    """
    
    # High impact events
    HIGH_IMPACT_EVENTS = [
        'FOMC', 'NFP', 'CPI', 'PPI', 'GDP', 'Retail Sales',
        'ECB', 'BOE', 'BOJ', 'RBA', 'RBNZ', 'BOC',
        'Employment', 'Unemployment', 'Interest Rate',
        'PMI', 'Trade Balance', 'Consumer Confidence',
    ]
    
    # Currency mapping
    CURRENCY_EVENTS = {
        'USD': ['FOMC', 'NFP', 'CPI', 'PPI', 'GDP', 'Retail Sales'],
        'EUR': ['ECB', 'CPI', 'GDP', 'PMI'],
        'GBP': ['BOE', 'CPI', 'GDP', 'Employment'],
        'JPY': ['BOJ', 'CPI', 'GDP'],
        'AUD': ['RBA', 'Employment', 'CPI'],
        'NZD': ['RBNZ', 'GDP', 'Employment'],
        'CAD': ['BOC', 'Employment', 'CPI'],
        'CHF': ['SNB', 'CPI'],
        'XAU': ['FOMC', 'NFP', 'CPI'],  # Gold affected by USD events
        'XAG': ['FOMC', 'NFP', 'CPI'],  # Silver affected by USD events
    }
    
    def check_news_risk(self, pair: str) -> Dict[str, Any]:
        """
        Check news risk for a currency pair.
        
        Args:
            pair: Currency pair (e.g., 'XAUUSD')
            
        Returns:
            News risk assessment
        """
        pair = pair.upper().replace('/', '')
        
        # Get affected currencies
        affected_currencies = self._get_affected_currencies(pair)
        
        # Get upcoming events (simulated)
        upcoming_events = self._get_upcoming_events(affected_currencies)
        
        # Determine risk level
        risk_assessment = self._assess_risk(upcoming_events)
        
        return {
            'pair': pair,
            'affected_currencies': affected_currencies,
            'upcoming_events': upcoming_events,
            'risk_level': risk_assessment['level'],
            'blocked': risk_assessment['blocked'],
            'caution': risk_assessment['caution'],
            'clear': risk_assessment['clear'],
            'next_high_impact': risk_assessment['next_high_impact'],
            'minutes_to_event': risk_assessment['minutes_to_event'],
            'recommendation': risk_assessment['recommendation'],
        }
    
    def _get_affected_currencies(self, pair: str) -> List[str]:
        """Get currencies affected by the pair."""
        currencies = []
        
        # Extract base and quote currencies
        if pair.startswith('XAU'):
            currencies.append('XAU')
            currencies.append('USD')
        elif pair.startswith('XAG'):
            currencies.append('XAG')
            currencies.append('USD')
        else:
            # Standard forex pair
            if len(pair) >= 6:
                currencies.append(pair[:3])
                currencies.append(pair[3:6])
        
        return currencies
    
    def _get_upcoming_events(self, currencies: List[str]) -> List[Dict[str, Any]]:
        """
        Get upcoming events for affected currencies.
        
        In production, this would fetch from ForexFactory API.
        """
        events = []
        now = datetime.utcnow()
        
        # Simulate upcoming events
        for currency in currencies:
            currency_events = self.CURRENCY_EVENTS.get(currency, [])
            
            for event_name in currency_events:
                # Random chance of event being scheduled
                if random.random() > 0.7:
                    # Random time in next 24 hours
                    minutes_ahead = random.randint(30, 1440)
                    event_time = now + timedelta(minutes=minutes_ahead)
                    
                    impact = random.choice(['HIGH', 'MEDIUM', 'LOW'])
                    
                    events.append({
                        'name': event_name,
                        'currency': currency,
                        'time': event_time.strftime('%Y-%m-%d %H:%M UTC'),
                        'minutes_away': minutes_ahead,
                        'impact': impact,
                        'is_red': impact == 'HIGH',
                    })
        
        # Sort by time
        events.sort(key=lambda x: x['minutes_away'])
        
        return events
    
    def _assess_risk(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Assess overall news risk.
        """
        # Find nearest high-impact event
        red_events = [e for e in events if e.get('is_red', False)]
        
        if not red_events:
            return {
                'level': 'CLEAR',
                'blocked': False,
                'caution': False,
                'clear': True,
                'next_high_impact': None,
                'minutes_to_event': None,
                'recommendation': 'No high-impact news - safe to trade',
            }
        
        nearest_red = red_events[0]
        minutes_away = nearest_red['minutes_away']
        
        if minutes_away < 60:
            return {
                'level': 'BLOCKED',
                'blocked': True,
                'caution': False,
                'clear': False,
                'next_high_impact': nearest_red,
                'minutes_to_event': minutes_away,
                'recommendation': f"BLOCKED: {nearest_red['name']} in {minutes_away} minutes - DO NOT TRADE",
            }
        elif minutes_away < 120:
            return {
                'level': 'CAUTION',
                'blocked': False,
                'caution': True,
                'clear': False,
                'next_high_impact': nearest_red,
                'minutes_to_event': minutes_away,
                'recommendation': f"CAUTION: {nearest_red['name']} in {minutes_away} minutes - reduce position size",
            }
        else:
            return {
                'level': 'CLEAR',
                'blocked': False,
                'caution': False,
                'clear': True,
                'next_high_impact': nearest_red,
                'minutes_to_event': minutes_away,
                'recommendation': f"Clear to trade - next event: {nearest_red['name']} in {minutes_away} minutes",
            }
    
    def get_weekly_calendar(self, currencies: List[str] = None) -> List[Dict[str, Any]]:
        """
        Get full weekly calendar.
        
        In production, this would fetch from ForexFactory.
        """
        if currencies is None:
            currencies = ['USD', 'EUR', 'GBP', 'JPY', 'AUD', 'CAD']
        
        events = []
        now = datetime.utcnow()
        
        # Generate events for the week
        for day_offset in range(7):
            day = now + timedelta(days=day_offset)
            
            for currency in currencies:
                currency_events = self.CURRENCY_EVENTS.get(currency, [])
                
                for event_name in currency_events:
                    if random.random() > 0.8:
                        hour = random.randint(8, 18)
                        event_time = day.replace(hour=hour, minute=random.choice([0, 30]))
                        
                        events.append({
                            'date': event_time.strftime('%Y-%m-%d'),
                            'time': event_time.strftime('%H:%M'),
                            'currency': currency,
                            'event': event_name,
                            'impact': random.choice(['HIGH', 'MEDIUM', 'LOW']),
                            'forecast': random.choice(['Better', 'Worse', 'Same', 'N/A']),
                        })
        
        events.sort(key=lambda x: (x['date'], x['time']))
        return events
