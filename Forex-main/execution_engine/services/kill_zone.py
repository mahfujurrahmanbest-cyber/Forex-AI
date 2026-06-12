"""Kill Zone Engine Service."""
from datetime import datetime, timezone
from typing import Dict, Any


class KillZoneEngine:
    """
    Trading Session and Kill Zone Analysis.
    
    Kill Zones are optimal trading times:
    - London Kill Zone: 07:00-10:00 UTC
    - New York Kill Zone: 12:00-15:00 UTC
    - London/NY Overlap: 12:00-16:00 UTC (BEST)
    """
    
    # Session times (UTC)
    SESSIONS = {
        'SYDNEY': {'start': 21, 'end': 6, 'score': 4},
        'TOKYO': {'start': 0, 'end': 9, 'score': 6},
        'LONDON': {'start': 7, 'end': 16, 'score': 9},
        'NEW_YORK': {'start': 12, 'end': 21, 'score': 9},
    }
    
    # Kill zones (UTC)
    KILL_ZONES = {
        'LONDON_KZ': {'start': 7, 'end': 10, 'score': 9},
        'NEW_YORK_KZ': {'start': 12, 'end': 15, 'score': 9},
        'OVERLAP': {'start': 12, 'end': 16, 'score': 10},
    }
    
    # Dead zones (low liquidity)
    DEAD_ZONES = {
        'LATE_NY': {'start': 19, 'end': 21, 'score': 2},
        'EARLY_SYDNEY': {'start': 21, 'end': 23, 'score': 3},
    }
    
    def get_current_session(self) -> Dict[str, Any]:
        """
        Get current trading session and kill zone status.
        
        Returns:
            Session analysis with scores
        """
        now = datetime.now(timezone.utc)
        hour = now.hour
        
        # Determine active sessions
        active_sessions = self._get_active_sessions(hour)
        
        # Check kill zones
        kill_zone_status = self._check_kill_zones(hour)
        
        # Check for overlap
        is_overlap = 'LONDON' in active_sessions and 'NEW_YORK' in active_sessions
        
        # Calculate session score
        session_score = self._calculate_session_score(hour, active_sessions, is_overlap)
        
        # Determine if it's a dead zone
        is_dead_zone = self._is_dead_zone(hour)
        
        return {
            'current_time_utc': now.strftime('%Y-%m-%d %H:%M:%S UTC'),
            'hour_utc': hour,
            'active_sessions': active_sessions,
            'is_overlap': is_overlap,
            'kill_zone': kill_zone_status,
            'is_kill_zone': kill_zone_status['active'],
            'is_dead_zone': is_dead_zone,
            'session_score': session_score,
            'recommendation': self._get_recommendation(session_score, is_dead_zone, kill_zone_status),
        }
    
    def _get_active_sessions(self, hour: int) -> list:
        """Get list of currently active sessions."""
        active = []
        
        for session, times in self.SESSIONS.items():
            start = times['start']
            end = times['end']
            
            if start <= end:
                if start <= hour < end:
                    active.append(session)
            else:  # Crosses midnight
                if hour >= start or hour < end:
                    active.append(session)
        
        return active
    
    def _check_kill_zones(self, hour: int) -> Dict[str, Any]:
        """Check if currently in a kill zone."""
        active_kz = None
        kz_score = 0
        
        for kz_name, times in self.KILL_ZONES.items():
            if times['start'] <= hour < times['end']:
                active_kz = kz_name
                kz_score = times['score']
                break
        
        return {
            'active': active_kz is not None,
            'name': active_kz,
            'score': kz_score,
            'london_kz': 7 <= hour < 10,
            'ny_kz': 12 <= hour < 15,
            'overlap_kz': 12 <= hour < 16,
        }
    
    def _calculate_session_score(self, hour: int, active_sessions: list, 
                                  is_overlap: bool) -> Dict[str, Any]:
        """Calculate session quality score (0-10)."""
        if is_overlap:
            score = 10
            quality = 'OPTIMAL'
        elif 'LONDON' in active_sessions or 'NEW_YORK' in active_sessions:
            # Check if in kill zone
            if 7 <= hour < 10 or 12 <= hour < 15:
                score = 9
                quality = 'EXCELLENT'
            else:
                score = 7
                quality = 'GOOD'
        elif 'TOKYO' in active_sessions:
            score = 6
            quality = 'MODERATE'
        elif 'SYDNEY' in active_sessions:
            score = 4
            quality = 'LOW'
        else:
            score = 2
            quality = 'POOR'
        
        return {
            'score': score,
            'max_score': 10,
            'quality': quality,
            'tradeable': score >= 6,
        }
    
    def _is_dead_zone(self, hour: int) -> bool:
        """Check if currently in a dead zone."""
        for dz_name, times in self.DEAD_ZONES.items():
            if times['start'] <= hour < times['end']:
                return True
        return False
    
    def _get_recommendation(self, session_score: Dict, is_dead_zone: bool,
                            kill_zone: Dict) -> str:
        """Get trading recommendation based on session."""
        if is_dead_zone:
            return 'AVOID: Dead zone - low liquidity, wide spreads'
        
        if kill_zone['overlap_kz']:
            return 'OPTIMAL: London/NY overlap - best liquidity and volatility'
        
        if kill_zone['london_kz']:
            return 'EXCELLENT: London kill zone - high volatility expected'
        
        if kill_zone['ny_kz']:
            return 'EXCELLENT: New York kill zone - high volatility expected'
        
        score = session_score['score']
        if score >= 7:
            return 'GOOD: Active session - suitable for trading'
        elif score >= 5:
            return 'MODERATE: Reduced volatility - be selective'
        else:
            return 'POOR: Low activity - consider waiting for better session'
    
    def get_next_kill_zone(self) -> Dict[str, Any]:
        """Get information about the next kill zone."""
        now = datetime.now(timezone.utc)
        hour = now.hour
        
        # Find next kill zone
        kill_zones_ordered = [
            ('LONDON_KZ', 7),
            ('NEW_YORK_KZ', 12),
            ('OVERLAP', 12),
        ]
        
        for kz_name, start_hour in kill_zones_ordered:
            if hour < start_hour:
                hours_until = start_hour - hour
                return {
                    'name': kz_name,
                    'starts_at': f"{start_hour:02d}:00 UTC",
                    'hours_until': hours_until,
                    'minutes_until': hours_until * 60,
                }
        
        # Next day's London KZ
        hours_until = (24 - hour) + 7
        return {
            'name': 'LONDON_KZ',
            'starts_at': '07:00 UTC (tomorrow)',
            'hours_until': hours_until,
            'minutes_until': hours_until * 60,
        }
