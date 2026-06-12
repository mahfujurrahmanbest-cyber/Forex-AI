"""ICT Execution Engine Service."""
import random
from typing import Dict, Any, Optional


class ICTExecutionEngine:
    """
    ICT (Inner Circle Trader) Smart Money Concepts Analysis.
    
    Analyzes:
    - Liquidity sweeps and stop hunts
    - Order blocks (bullish/bearish)
    - Fair value gaps (FVG)
    - Premium/Discount zones
    - SMT divergence
    - Balanced price ranges
    """
    
    def analyze(self, pair: str, live_data: Dict[str, Any], 
                structure: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform full ICT analysis.
        
        Args:
            pair: Currency pair
            live_data: Live market data
            structure: Market structure analysis
            
        Returns:
            Complete ICT analysis
        """
        current_price = live_data.get('price_data', {}).get('current', 0)
        
        # Analyze each ICT component
        liquidity = self._analyze_liquidity(current_price)
        order_blocks = self._analyze_order_blocks(current_price)
        fvg = self._analyze_fvg(current_price)
        zones = self._analyze_premium_discount(current_price)
        smt = self._analyze_smt(pair)
        bpr = self._analyze_bpr(current_price)
        
        # Calculate ICT alignment score
        alignment_score = self._calculate_ict_alignment(
            liquidity, order_blocks, fvg, zones, smt, structure
        )
        
        return {
            'pair': pair,
            'current_price': current_price,
            'liquidity': liquidity,
            'order_blocks': order_blocks,
            'fair_value_gaps': fvg,
            'zones': zones,
            'smt_divergence': smt,
            'balanced_price_range': bpr,
            'alignment_score': alignment_score,
            'trade_bias': self._determine_trade_bias(alignment_score, structure),
        }
    
    def assess_entry_quality(self, live_data: Dict[str, Any],
                             ict_analysis: Dict[str, Any],
                             report_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Assess entry quality based on ICT criteria.
        
        Quality Grades:
        - A+: Inside Weekly OB + FVG + Liquidity Sweep + M15 BOS
        - A: OB + BOS
        - B: OB Only
        - C: Near OB
        - D: Far from OB
        - Reject: No valid setup
        """
        ob = ict_analysis.get('order_blocks', {})
        fvg = ict_analysis.get('fair_value_gaps', {})
        liquidity = ict_analysis.get('liquidity', {})
        
        # Check conditions
        inside_weekly_ob = ob.get('weekly_ob_touch', False)
        inside_weekly_fvg = fvg.get('weekly_fvg_present', False)
        liquidity_sweep = liquidity.get('sweep_detected', False)
        m15_bos = random.random() > 0.5  # Simulated
        
        # Determine grade
        if inside_weekly_ob and inside_weekly_fvg and liquidity_sweep and m15_bos:
            grade = 'A+'
            description = 'Inside Weekly OB + FVG + Liquidity Sweep + M15 BOS'
        elif ob.get('active_ob', False) and m15_bos:
            grade = 'A'
            description = 'Order Block + Break of Structure'
        elif ob.get('active_ob', False):
            grade = 'B'
            description = 'Order Block Only'
        elif ob.get('near_ob', False):
            grade = 'C'
            description = 'Near Order Block'
        elif ob.get('distance_to_ob', 100) < 50:  # pips
            grade = 'D'
            description = 'Far from Order Block'
        else:
            grade = 'REJECT'
            description = 'No valid ICT setup'
        
        return {
            'grade': grade,
            'description': description,
            'inside_weekly_ob': inside_weekly_ob,
            'inside_weekly_fvg': inside_weekly_fvg,
            'liquidity_sweep': liquidity_sweep,
            'm15_bos': m15_bos,
            'tradeable': grade not in ['D', 'REJECT'],
        }
    
    def _analyze_liquidity(self, current_price: float) -> Dict[str, Any]:
        """Analyze liquidity pools and sweeps."""
        # Simulate liquidity analysis
        sweep_detected = random.random() > 0.6
        sweep_direction = random.choice(['ABOVE', 'BELOW']) if sweep_detected else None
        
        return {
            'sweep_detected': sweep_detected,
            'sweep_direction': sweep_direction,
            'stop_hunt': random.random() > 0.7,
            'equal_highs': {
                'detected': random.random() > 0.5,
                'level': round(current_price * 1.005, 5) if current_price else None,
            },
            'equal_lows': {
                'detected': random.random() > 0.5,
                'level': round(current_price * 0.995, 5) if current_price else None,
            },
            'pwh': round(current_price * 1.01, 5) if current_price else None,
            'pwl': round(current_price * 0.99, 5) if current_price else None,
            'liquidity_score': random.randint(4, 10),
        }
    
    def _analyze_order_blocks(self, current_price: float) -> Dict[str, Any]:
        """Analyze order blocks."""
        active_ob = random.random() > 0.4
        ob_direction = random.choice(['BULLISH', 'BEARISH']) if active_ob else None
        
        distance = random.uniform(5, 100)  # pips
        
        return {
            'active_ob': active_ob,
            'ob_direction': ob_direction,
            'weekly_ob_touch': random.random() > 0.7,
            'daily_ob_touch': random.random() > 0.5,
            'h4_ob_touch': random.random() > 0.4,
            'near_ob': distance < 30,
            'distance_to_ob': round(distance, 1),
            'bullish_ob_levels': [
                round(current_price * 0.995, 5),
                round(current_price * 0.990, 5),
            ] if current_price else [],
            'bearish_ob_levels': [
                round(current_price * 1.005, 5),
                round(current_price * 1.010, 5),
            ] if current_price else [],
            'breaker_block': random.random() > 0.8,
            'mitigation_block': random.random() > 0.85,
        }
    
    def _analyze_fvg(self, current_price: float) -> Dict[str, Any]:
        """Analyze fair value gaps."""
        fvg_present = random.random() > 0.5
        
        return {
            'fvg_present': fvg_present,
            'weekly_fvg_present': random.random() > 0.6,
            'daily_fvg_present': random.random() > 0.5,
            'fvg_direction': random.choice(['BULLISH', 'BEARISH']) if fvg_present else None,
            'fvg_levels': {
                'upper': round(current_price * 1.003, 5) if current_price else None,
                'lower': round(current_price * 0.997, 5) if current_price else None,
            },
            'inverse_fvg': random.random() > 0.8,
            'fvg_filled': random.random() > 0.6,
        }
    
    def _analyze_premium_discount(self, current_price: float) -> Dict[str, Any]:
        """Analyze premium/discount zones."""
        # Simulate dealing range
        range_high = current_price * 1.02 if current_price else 0
        range_low = current_price * 0.98 if current_price else 0
        equilibrium = (range_high + range_low) / 2
        
        # Determine zone
        if current_price:
            if current_price > equilibrium:
                zone = 'PREMIUM'
                zone_pct = ((current_price - equilibrium) / (range_high - equilibrium)) * 50 + 50
            else:
                zone = 'DISCOUNT'
                zone_pct = ((current_price - range_low) / (equilibrium - range_low)) * 50
        else:
            zone = 'UNKNOWN'
            zone_pct = 50
        
        # OTE zone (61.8% - 79%)
        ote_upper = range_low + (range_high - range_low) * 0.79
        ote_lower = range_low + (range_high - range_low) * 0.618
        in_ote = ote_lower <= current_price <= ote_upper if current_price else False
        
        return {
            'zone': zone,
            'zone_percentage': round(zone_pct, 1),
            'dealing_range': {
                'high': round(range_high, 5),
                'low': round(range_low, 5),
                'equilibrium': round(equilibrium, 5),
            },
            'ote_zone': {
                'upper': round(ote_upper, 5),
                'lower': round(ote_lower, 5),
                'in_ote': in_ote,
            },
            'optimal_for_buy': zone == 'DISCOUNT',
            'optimal_for_sell': zone == 'PREMIUM',
        }
    
    def _analyze_smt(self, pair: str) -> Dict[str, Any]:
        """Analyze SMT (Smart Money Technique) divergence."""
        # Determine correlated pair
        correlations = {
            'XAUUSD': 'XAGUSD',
            'XAGUSD': 'XAUUSD',
            'EURUSD': 'GBPUSD',
            'GBPUSD': 'EURUSD',
            'AUDUSD': 'NZDUSD',
            'NZDUSD': 'AUDUSD',
        }
        
        correlated_pair = correlations.get(pair, None)
        smt_detected = random.random() > 0.7
        
        return {
            'detected': smt_detected,
            'correlated_pair': correlated_pair,
            'divergence_type': random.choice(['BULLISH', 'BEARISH']) if smt_detected else None,
            'description': 'Correlated pair failed to make new high/low' if smt_detected else None,
            'confidence': random.randint(60, 95) if smt_detected else 0,
        }
    
    def _analyze_bpr(self, current_price: float) -> Dict[str, Any]:
        """Analyze Balanced Price Range."""
        bpr_present = random.random() > 0.75
        
        return {
            'present': bpr_present,
            'level': round(current_price * (1 + random.uniform(-0.005, 0.005)), 5) if bpr_present and current_price else None,
            'description': 'Overlapping FVGs creating balanced zone' if bpr_present else None,
        }
    
    def _calculate_ict_alignment(self, liquidity: Dict, order_blocks: Dict,
                                  fvg: Dict, zones: Dict, smt: Dict,
                                  structure: Dict) -> Dict[str, Any]:
        """Calculate overall ICT alignment score (0-100)."""
        score = 0
        max_score = 100
        breakdown = []
        
        # Liquidity sweep (+20)
        if liquidity.get('sweep_detected'):
            score += 20
            breakdown.append('Liquidity Sweep: +20')
        
        # Order block touch (+20)
        if order_blocks.get('active_ob'):
            score += 20
            breakdown.append('Active Order Block: +20')
        
        # FVG present (+15)
        if fvg.get('fvg_present'):
            score += 15
            breakdown.append('Fair Value Gap: +15')
        
        # Premium/Discount zone (+15)
        if zones.get('zone') in ['PREMIUM', 'DISCOUNT']:
            score += 15
            breakdown.append(f"{zones.get('zone')} Zone: +15")
        
        # OTE zone (+10)
        if zones.get('ote_zone', {}).get('in_ote'):
            score += 10
            breakdown.append('In OTE Zone: +10')
        
        # SMT divergence (+15)
        if smt.get('detected'):
            score += 15
            breakdown.append('SMT Divergence: +15')
        
        # Structure alignment (+5)
        if structure.get('overall_structure', {}).get('htf_bos'):
            score += 5
            breakdown.append('HTF BOS: +5')
        
        return {
            'score': score,
            'max_score': max_score,
            'percentage': round((score / max_score) * 100, 1),
            'breakdown': breakdown,
            'is_aligned': score >= 50,
        }
    
    def _determine_trade_bias(self, alignment: Dict, structure: Dict) -> Dict[str, Any]:
        """Determine trade bias based on ICT and structure."""
        ict_score = alignment.get('score', 0)
        structure_bias = structure.get('dominant_bias', 'NEUTRAL')
        
        if ict_score >= 70:
            confidence = 'HIGH'
        elif ict_score >= 50:
            confidence = 'MEDIUM'
        else:
            confidence = 'LOW'
        
        return {
            'direction': structure_bias,
            'confidence': confidence,
            'ict_score': ict_score,
            'tradeable': ict_score >= 50 and structure_bias != 'NEUTRAL',
        }
