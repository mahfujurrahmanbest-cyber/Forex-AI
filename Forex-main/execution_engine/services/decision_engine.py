"""Decision Engine Service - Makes final trade decision."""
from typing import Dict, Any, Optional
from datetime import datetime


class DecisionEngine:
    """
    Final Decision Engine.
    
    Makes exactly ONE decision:
    - 🟢 EXECUTE NOW
    - 🟡 WAIT FOR CONFIRMATION
    - 🟠 MONITOR ONLY
    - 🔴 ABORT
    
    Priority Order:
    1. News
    2. Live Market
    3. Weekly Report
    4. ICT
    5. DXY
    6. Session
    7. Trade Quality
    """
    
    # Decision thresholds
    EXECUTE_THRESHOLD = {
        'instant_score': 22,
        'trade_quality': 85,
    }
    
    WAIT_THRESHOLD = {
        'instant_score_min': 14,
        'instant_score_max': 21,
    }
    
    def make_decision(self, report_data: Optional[Dict],
                      live_data: Dict[str, Any],
                      direction: str,
                      instant_score: Dict[str, Any],
                      trade_quality: Dict[str, Any],
                      news_result: Dict[str, Any],
                      ict_analysis: Dict[str, Any],
                      dxy_analysis: Dict[str, Any],
                      pro_test: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make final trade decision.
        
        Returns exactly ONE decision with full reasoning.
        """
        direction = direction.upper()
        
        # Step 1: Check blockers (immediate ABORT conditions)
        blockers = self._check_blockers(news_result, instant_score, trade_quality, pro_test)
        
        if blockers['has_blocker']:
            return self._create_decision(
                'ABORT',
                blockers['reason'],
                instant_score,
                trade_quality,
                blockers['details']
            )
        
        # Step 2: Check live market override
        override = self._check_live_override(report_data, live_data, direction, ict_analysis)
        
        if override['conflict']:
            return self._create_decision(
                'WAIT',
                override['reason'],
                instant_score,
                trade_quality,
                override['details']
            )
        
        # Step 3: Check for EXECUTE NOW conditions
        execute_check = self._check_execute_conditions(
            instant_score, trade_quality, news_result,
            ict_analysis, dxy_analysis, pro_test
        )
        
        if execute_check['ready']:
            # Apply confidence boost if everything aligns
            confidence_boost = 0
            if override.get('full_alignment'):
                confidence_boost = 10
            
            return self._create_decision(
                'EXECUTE',
                'All criteria met - Trade approved for execution',
                instant_score,
                trade_quality,
                execute_check['details'],
                confidence_boost=confidence_boost
            )
        
        # Step 4: Check for WAIT conditions
        wait_check = self._check_wait_conditions(instant_score, ict_analysis)
        
        if wait_check['should_wait']:
            return self._create_decision(
                'WAIT',
                wait_check['reason'],
                instant_score,
                trade_quality,
                wait_check['details']
            )
        
        # Step 5: Check for MONITOR conditions
        monitor_check = self._check_monitor_conditions(report_data, ict_analysis)
        
        if monitor_check['should_monitor']:
            return self._create_decision(
                'MONITOR',
                monitor_check['reason'],
                instant_score,
                trade_quality,
                monitor_check['details']
            )
        
        # Default: ABORT if nothing else matches
        return self._create_decision(
            'ABORT',
            'Setup does not meet minimum criteria',
            instant_score,
            trade_quality,
            {'reason': 'No valid setup conditions met'}
        )
    
    def _check_blockers(self, news_result: Dict, instant_score: Dict,
                        trade_quality: Dict, pro_test: Dict) -> Dict[str, Any]:
        """
        Check for immediate blocking conditions.
        """
        blockers = []
        
        # News blocked
        if news_result.get('blocked'):
            blockers.append({
                'type': 'NEWS_BLOCKED',
                'reason': f"High-impact news in {news_result.get('minutes_to_event', 'N/A')} minutes",
                'severity': 'CRITICAL',
            })
        
        # Instant score too low
        if instant_score.get('total', 0) < 14:
            blockers.append({
                'type': 'SCORE_TOO_LOW',
                'reason': f"Instant score {instant_score.get('total')}/28 below minimum 14",
                'severity': 'HIGH',
            })
        
        # Trade quality too low
        if trade_quality.get('total', 0) < 70:
            blockers.append({
                'type': 'QUALITY_TOO_LOW',
                'reason': f"Trade quality {trade_quality.get('total')}/100 below minimum 70",
                'severity': 'HIGH',
            })
        
        # Professional test failed
        if not pro_test.get('all_pass'):
            blockers.append({
                'type': 'PRO_TEST_FAILED',
                'reason': pro_test.get('reason', 'Professional criteria not met'),
                'severity': 'MEDIUM',
            })
        
        return {
            'has_blocker': len(blockers) > 0,
            'blockers': blockers,
            'reason': blockers[0]['reason'] if blockers else None,
            'details': {'blockers': blockers},
        }
    
    def _check_live_override(self, report_data: Optional[Dict],
                              live_data: Dict, direction: str,
                              ict_analysis: Dict) -> Dict[str, Any]:
        """
        Check if live market conflicts with weekly report.
        """
        if not report_data or not report_data.get('parsed'):
            return {
                'conflict': False,
                'full_alignment': False,
                'reason': None,
                'details': {'note': 'No weekly report to compare'},
            }
        
        report_direction = report_data.get('weekly_direction', 'NEUTRAL')
        live_bias = ict_analysis.get('trade_bias', {}).get('direction', 'NEUTRAL')
        
        # Check for conflict
        if direction != 'NOT SURE':
            if report_direction and report_direction != direction:
                return {
                    'conflict': True,
                    'full_alignment': False,
                    'reason': f"Your direction ({direction}) conflicts with weekly report ({report_direction})",
                    'details': {
                        'user_direction': direction,
                        'report_direction': report_direction,
                        'live_bias': live_bias,
                    },
                }
            
            if live_bias and live_bias != direction and live_bias != 'NEUTRAL':
                return {
                    'conflict': True,
                    'full_alignment': False,
                    'reason': f"Your direction ({direction}) conflicts with live market ({live_bias})",
                    'details': {
                        'user_direction': direction,
                        'report_direction': report_direction,
                        'live_bias': live_bias,
                    },
                }
        
        # Check for full alignment
        full_alignment = (
            report_direction == live_bias and
            (direction == 'NOT SURE' or direction == report_direction)
        )
        
        return {
            'conflict': False,
            'full_alignment': full_alignment,
            'reason': None,
            'details': {
                'report_direction': report_direction,
                'live_bias': live_bias,
                'aligned': full_alignment,
            },
        }
    
    def _check_execute_conditions(self, instant_score: Dict,
                                   trade_quality: Dict, news_result: Dict,
                                   ict_analysis: Dict, dxy_analysis: Dict,
                                   pro_test: Dict) -> Dict[str, Any]:
        """
        Check if all EXECUTE NOW conditions are met.
        
        Requirements:
        - Score >= 22
        - Trade Quality >= 85
        - News Clear
        - Weekly Valid
        - Live Valid
        - ICT Valid
        - DXY Supports
        """
        conditions = {
            'score_met': instant_score.get('total', 0) >= 22,
            'quality_met': trade_quality.get('total', 0) >= 85,
            'news_clear': news_result.get('clear', False),
            'ict_valid': ict_analysis.get('alignment_score', {}).get('score', 0) >= 50,
            'dxy_supports': dxy_analysis.get('supports_trade', False) or 
                           dxy_analysis.get('classification', {}).get('status') == 'NEUTRAL',
            'pro_test_pass': pro_test.get('all_pass', False),
        }
        
        all_met = all(conditions.values())
        
        return {
            'ready': all_met,
            'conditions': conditions,
            'met_count': sum(1 for v in conditions.values() if v),
            'total_conditions': len(conditions),
            'details': conditions,
        }
    
    def _check_wait_conditions(self, instant_score: Dict,
                                ict_analysis: Dict) -> Dict[str, Any]:
        """
        Check if WAIT FOR CONFIRMATION conditions are met.
        
        Requirements:
        - Score 14-21
        - Need BOS/Sweep/Confirmation
        """
        score = instant_score.get('total', 0)
        
        if 14 <= score <= 21:
            # Determine what's needed
            needs = []
            
            if not ict_analysis.get('liquidity', {}).get('sweep_detected'):
                needs.append('Liquidity sweep')
            
            if not ict_analysis.get('order_blocks', {}).get('active_ob'):
                needs.append('Order block touch')
            
            ict_score = ict_analysis.get('alignment_score', {}).get('score', 0)
            if ict_score < 60:
                needs.append('Better ICT alignment')
            
            return {
                'should_wait': True,
                'reason': f"Score {score}/28 - waiting for: {', '.join(needs) if needs else 'confirmation'}",
                'details': {
                    'score': score,
                    'needs': needs,
                },
            }
        
        return {
            'should_wait': False,
            'reason': None,
            'details': {},
        }
    
    def _check_monitor_conditions(self, report_data: Optional[Dict],
                                   ict_analysis: Dict) -> Dict[str, Any]:
        """
        Check if MONITOR ONLY conditions are met.
        
        Requirements:
        - Good weekly bias
        - Price not at zone
        - Watchlist setup
        """
        # Check if report has good bias but price not at entry
        if report_data and report_data.get('parsed'):
            classification = report_data.get('classification', '')
            
            if classification in ['WATCHLIST', 'APPROVED']:
                zones = ict_analysis.get('zones', {})
                zone = zones.get('zone', 'EQUILIBRIUM')
                
                if zone == 'EQUILIBRIUM':
                    return {
                        'should_monitor': True,
                        'reason': 'Good weekly bias but price at equilibrium - wait for discount/premium zone',
                        'details': {
                            'classification': classification,
                            'current_zone': zone,
                        },
                    }
        
        return {
            'should_monitor': False,
            'reason': None,
            'details': {},
        }
    
    def _create_decision(self, decision: str, reason: str,
                         instant_score: Dict, trade_quality: Dict,
                         details: Dict, confidence_boost: int = 0) -> Dict[str, Any]:
        """
        Create final decision object.
        """
        # Map decision to emoji and color
        decision_map = {
            'EXECUTE': {
                'emoji': '🟢',
                'color': 'green',
                'action': 'EXECUTE NOW',
                'priority': 1,
            },
            'WAIT': {
                'emoji': '🟡',
                'color': 'yellow',
                'action': 'WAIT FOR CONFIRMATION',
                'priority': 2,
            },
            'MONITOR': {
                'emoji': '🟠',
                'color': 'orange',
                'action': 'MONITOR ONLY',
                'priority': 3,
            },
            'ABORT': {
                'emoji': '🔴',
                'color': 'red',
                'action': 'ABORT',
                'priority': 4,
            },
        }
        
        decision_info = decision_map.get(decision, decision_map['ABORT'])
        
        # Calculate confidence
        base_confidence = min(100, (
            (instant_score.get('total', 0) / 28) * 50 +
            (trade_quality.get('total', 0) / 100) * 50
        ))
        final_confidence = min(100, base_confidence + confidence_boost)
        
        return {
            'decision': decision,
            'action': decision_info['action'],
            'emoji': decision_info['emoji'],
            'color': decision_info['color'],
            'reason': reason,
            'confidence': round(final_confidence, 1),
            'instant_score': instant_score.get('total', 0),
            'trade_quality': trade_quality.get('total', 0),
            'details': details,
            'timestamp': datetime.utcnow().isoformat(),
            'can_trade': decision == 'EXECUTE',
            'needs_confirmation': decision == 'WAIT',
            'should_monitor': decision == 'MONITOR',
            'is_blocked': decision == 'ABORT',
        }
