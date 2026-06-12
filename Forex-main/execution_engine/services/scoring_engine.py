"""Scoring Engine Service - Calculates all trade scores."""
from typing import Dict, Any, Optional


class ScoringEngine:
    """
    Comprehensive Scoring Engine.
    
    Calculates:
    - Live MTF Score (0-100)
    - Trade Quality Score (0-100)
    - Instant Score (/28)
    - Professional Trader Test
    """
    
    # MTF Weights
    MTF_WEIGHTS = {
        'MONTHLY': 20,
        'WEEKLY': 20,
        'DAILY': 20,
        'H4': 15,
        'H1': 10,
        'M15': 8,
        'M5': 7,
    }
    
    # Trade Quality Weights
    QUALITY_WEIGHTS = {
        'weekly_report': 20,
        'live_mtf': 20,
        'ict_alignment': 20,
        'liquidity': 15,
        'dxy': 10,
        'session': 5,
        'news': 5,
        'correlation': 5,
    }
    
    def calculate_mtf_score(self, structure_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate Live MTF Alignment Score (0-100).
        
        Minimum 50 required for trade approval.
        """
        tf_analysis = structure_analysis.get('timeframe_analysis', {})
        
        weighted_sum = 0
        total_weight = sum(self.MTF_WEIGHTS.values())
        aligned_count = 0
        dominant_direction = None
        
        # Count biases
        bullish_weight = 0
        bearish_weight = 0
        
        for tf, weight in self.MTF_WEIGHTS.items():
            tf_data = tf_analysis.get(tf, {})
            bias = tf_data.get('bias', 'NEUTRAL')
            
            if bias == 'BULLISH':
                bullish_weight += weight
                aligned_count += 1
            elif bias == 'BEARISH':
                bearish_weight += weight
        
        # Determine dominant direction and score
        if bullish_weight > bearish_weight:
            dominant_direction = 'BULLISH'
            alignment_score = (bullish_weight / total_weight) * 100
        elif bearish_weight > bullish_weight:
            dominant_direction = 'BEARISH'
            alignment_score = (bearish_weight / total_weight) * 100
        else:
            dominant_direction = 'NEUTRAL'
            alignment_score = 50
        
        return {
            'score': round(alignment_score, 1),
            'direction': dominant_direction,
            'bullish_weight': bullish_weight,
            'bearish_weight': bearish_weight,
            'aligned_timeframes': aligned_count,
            'total_timeframes': len(self.MTF_WEIGHTS),
            'meets_minimum': alignment_score >= 50,
            'interpretation': self._interpret_mtf_score(alignment_score),
        }
    
    def calculate_trade_quality(self, report_data: Optional[Dict],
                                 mtf_score: Dict[str, Any],
                                 ict_analysis: Dict[str, Any],
                                 dxy_analysis: Dict[str, Any],
                                 kill_zone: Dict[str, Any],
                                 news_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate Trade Quality Score (0-100).
        
        Components:
        - Weekly Report Alignment: 20
        - Live MTF Alignment: 20
        - ICT Alignment: 20
        - Liquidity: 15
        - DXY: 10
        - Session: 5
        - News: 5
        - Correlation: 5
        """
        scores = {}
        
        # Weekly Report Alignment (20 points)
        if report_data and report_data.get('parsed'):
            report_confidence = report_data.get('weekly_confidence', 0) or 0
            scores['weekly_report'] = min(20, (report_confidence / 100) * 20)
        else:
            scores['weekly_report'] = 10  # Neutral if no report
        
        # Live MTF Alignment (20 points)
        mtf_value = mtf_score.get('score', 50)
        scores['live_mtf'] = (mtf_value / 100) * 20
        
        # ICT Alignment (20 points)
        ict_score = ict_analysis.get('alignment_score', {}).get('score', 0)
        scores['ict_alignment'] = (ict_score / 100) * 20
        
        # Liquidity (15 points)
        liquidity_score = ict_analysis.get('liquidity', {}).get('liquidity_score', 5)
        scores['liquidity'] = (liquidity_score / 10) * 15
        
        # DXY (10 points)
        if dxy_analysis.get('supports_trade'):
            scores['dxy'] = 10
        elif dxy_analysis.get('classification', {}).get('status') == 'NEUTRAL':
            scores['dxy'] = 5
        else:
            scores['dxy'] = 0
        
        # Session (5 points)
        session_score = kill_zone.get('session_score', {}).get('score', 5)
        scores['session'] = (session_score / 10) * 5
        
        # News (5 points)
        if news_result.get('clear'):
            scores['news'] = 5
        elif news_result.get('caution'):
            scores['news'] = 2.5
        else:
            scores['news'] = 0
        
        # Correlation (5 points) - simplified
        scores['correlation'] = 3  # Default moderate
        
        # Calculate total
        total = sum(scores.values())
        
        return {
            'total': round(total, 1),
            'max_score': 100,
            'breakdown': {k: round(v, 1) for k, v in scores.items()},
            'interpretation': self._interpret_quality_score(total),
            'tradeable': total >= 70,
            'elite': total >= 90,
            'high_quality': total >= 80,
        }
    
    def professional_trader_test(self, trade_quality: Dict[str, Any],
                                  ict_analysis: Dict[str, Any],
                                  news_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Professional Trader Test.
        
        Asks:
        - Would FTMO approve?
        - Would a hedge fund trader enter?
        - Would a prop trader take this?
        - Would I take this if it was my only trade today?
        
        If ANY answer is NO -> ABORT
        """
        quality_score = trade_quality.get('total', 0)
        ict_score = ict_analysis.get('alignment_score', {}).get('score', 0)
        news_clear = news_result.get('clear', False)
        
        tests = {
            'ftmo_approve': quality_score >= 75 and news_clear,
            'hedge_fund_enter': quality_score >= 80 and ict_score >= 60,
            'prop_trader_take': quality_score >= 70 and ict_score >= 50,
            'only_trade_today': quality_score >= 85,
        }
        
        all_pass = all(tests.values())
        pass_count = sum(1 for v in tests.values() if v)
        
        return {
            'tests': tests,
            'all_pass': all_pass,
            'pass_count': pass_count,
            'total_tests': len(tests),
            'verdict': 'APPROVED' if all_pass else 'ABORT',
            'reason': self._get_test_failure_reason(tests) if not all_pass else 'All professional criteria met',
        }
    
    def calculate_instant_score(self, report_data: Optional[Dict],
                                 direction: str,
                                 mtf_score: Dict[str, Any],
                                 ict_analysis: Dict[str, Any],
                                 live_data: Dict[str, Any],
                                 dxy_analysis: Dict[str, Any],
                                 news_result: Dict[str, Any],
                                 kill_zone: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate Instant Score (/28).
        
        Scoring:
        - Weekly Direction Valid: +3
        - Approved In Weekly Report: +2
        - Sure Trade In Weekly Report: +1
        - Live MTF > 50: +3
        - Liquidity Sweep: +3
        - Inside OB/FVG: +2
        - BOS/CHOCH: +2
        - RSI Alignment: +2
        - MACD Alignment: +2
        - DXY Supports: +2
        - No News: +2
        - Prime Session: +1
        - Pivot Alignment: +1
        - DXY Unchanged: +1
        - Premium/Discount: +1
        
        Maximum = 28
        """
        scores = {}
        direction = direction.upper()
        
        # Weekly Direction Valid (+3)
        if report_data and report_data.get('parsed'):
            report_direction = report_data.get('weekly_direction', '')
            if report_direction == direction or direction == 'NOT SURE':
                scores['weekly_direction_valid'] = 3
            else:
                scores['weekly_direction_valid'] = 0
        else:
            scores['weekly_direction_valid'] = 1  # Partial if no report
        
        # Approved In Weekly Report (+2)
        if report_data and report_data.get('classification') in ['APPROVED', 'HIGH_TRADE', 'SURE_TRADE']:
            scores['approved_in_report'] = 2
        else:
            scores['approved_in_report'] = 0
        
        # Sure Trade In Weekly Report (+1)
        if report_data and report_data.get('classification') == 'SURE_TRADE':
            scores['sure_trade'] = 1
        else:
            scores['sure_trade'] = 0
        
        # Live MTF > 50 (+3)
        if mtf_score.get('score', 0) >= 50:
            scores['live_mtf'] = 3
        else:
            scores['live_mtf'] = 0
        
        # Liquidity Sweep (+3)
        if ict_analysis.get('liquidity', {}).get('sweep_detected'):
            scores['liquidity_sweep'] = 3
        else:
            scores['liquidity_sweep'] = 0
        
        # Inside OB/FVG (+2)
        ob_touch = ict_analysis.get('order_blocks', {}).get('active_ob', False)
        fvg_present = ict_analysis.get('fair_value_gaps', {}).get('fvg_present', False)
        if ob_touch or fvg_present:
            scores['inside_ob_fvg'] = 2
        else:
            scores['inside_ob_fvg'] = 0
        
        # BOS/CHOCH (+2)
        # Check from structure analysis in live_data
        scores['bos_choch'] = 2 if ict_analysis.get('alignment_score', {}).get('score', 0) >= 50 else 0
        
        # RSI Alignment (+2)
        tech_data = live_data.get('technical_data', {})
        rsi_data = tech_data.get('rsi', {})
        rsi_value = rsi_data.get('value', 50)
        if direction == 'BUY' and rsi_value < 40:
            scores['rsi_alignment'] = 2
        elif direction == 'SELL' and rsi_value > 60:
            scores['rsi_alignment'] = 2
        elif direction == 'NOT SURE':
            scores['rsi_alignment'] = 1
        else:
            scores['rsi_alignment'] = 0
        
        # MACD Alignment (+2)
        macd_data = tech_data.get('macd', {})
        macd_trend = macd_data.get('trend', 'NEUTRAL')
        if (direction == 'BUY' and macd_trend == 'BULLISH') or \
           (direction == 'SELL' and macd_trend == 'BEARISH'):
            scores['macd_alignment'] = 2
        elif direction == 'NOT SURE':
            scores['macd_alignment'] = 1
        else:
            scores['macd_alignment'] = 0
        
        # DXY Supports (+2)
        if dxy_analysis.get('supports_trade'):
            scores['dxy_supports'] = 2
        else:
            scores['dxy_supports'] = 0
        
        # No News (+2)
        if news_result.get('clear'):
            scores['no_news'] = 2
        elif news_result.get('caution'):
            scores['no_news'] = 1
        else:
            scores['no_news'] = 0
        
        # Prime Session (+1)
        if kill_zone.get('is_kill_zone') or kill_zone.get('is_overlap'):
            scores['prime_session'] = 1
        else:
            scores['prime_session'] = 0
        
        # Pivot Alignment (+1)
        scores['pivot_alignment'] = 1  # Simplified
        
        # DXY Unchanged (+1)
        if not dxy_analysis.get('report_comparison', {}).get('changed', True):
            scores['dxy_unchanged'] = 1
        else:
            scores['dxy_unchanged'] = 0
        
        # Premium/Discount (+1)
        zones = ict_analysis.get('zones', {})
        zone = zones.get('zone', 'EQUILIBRIUM')
        if (direction == 'BUY' and zone == 'DISCOUNT') or \
           (direction == 'SELL' and zone == 'PREMIUM'):
            scores['premium_discount'] = 1
        else:
            scores['premium_discount'] = 0
        
        # Calculate total
        total = sum(scores.values())
        
        return {
            'total': total,
            'max_score': 28,
            'percentage': round((total / 28) * 100, 1),
            'breakdown': scores,
            'meets_minimum': total >= 14,
            'execute_ready': total >= 22,
            'interpretation': self._interpret_instant_score(total),
        }
    
    def _interpret_mtf_score(self, score: float) -> str:
        """Interpret MTF score."""
        if score >= 85:
            return 'STRONG INSTITUTIONAL ALIGNMENT'
        elif score >= 70:
            return 'GOOD ALIGNMENT'
        elif score >= 50:
            return 'MODERATE ALIGNMENT'
        elif score >= 30:
            return 'WEAK ALIGNMENT'
        return 'POOR ALIGNMENT - AVOID'
    
    def _interpret_quality_score(self, score: float) -> str:
        """Interpret trade quality score."""
        if score >= 90:
            return 'ELITE - Institutional Grade Setup'
        elif score >= 80:
            return 'HIGH QUALITY - Strong Setup'
        elif score >= 70:
            return 'ACCEPTABLE - Proceed with Caution'
        return 'BELOW THRESHOLD - ABORT'
    
    def _interpret_instant_score(self, score: int) -> str:
        """Interpret instant score."""
        if score >= 22:
            return 'EXECUTE NOW - All criteria met'
        elif score >= 18:
            return 'STRONG SETUP - Minor confirmations needed'
        elif score >= 14:
            return 'WAIT FOR CONFIRMATION - Setup forming'
        elif score >= 10:
            return 'MONITOR ONLY - Not ready'
        return 'ABORT - Insufficient criteria'
    
    def _get_test_failure_reason(self, tests: Dict[str, bool]) -> str:
        """Get reason for professional test failure."""
        failures = [k for k, v in tests.items() if not v]
        
        reasons = {
            'ftmo_approve': 'Quality too low or news risk present',
            'hedge_fund_enter': 'ICT alignment insufficient',
            'prop_trader_take': 'Setup not meeting prop standards',
            'only_trade_today': 'Not confident enough for single trade',
        }
        
        return '; '.join([reasons.get(f, f) for f in failures])
