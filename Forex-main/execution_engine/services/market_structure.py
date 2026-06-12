"""Market Structure Analyzer Service."""
import random
from typing import Dict, Any, List


class MarketStructureAnalyzer:
    """
    Analyze market structure across multiple timeframes.
    
    Identifies:
    - Higher Highs (HH) / Higher Lows (HL) - Bullish
    - Lower Highs (LH) / Lower Lows (LL) - Bearish
    - Break of Structure (BOS)
    - Change of Character (CHOCH)
    - Market Structure Shift (MSS)
    """
    
    TIMEFRAMES = ['MONTHLY', 'WEEKLY', 'DAILY', 'H4', 'H1', 'M15', 'M5']
    
    TF_WEIGHTS = {
        'MONTHLY': 20,
        'WEEKLY': 20,
        'DAILY': 20,
        'H4': 15,
        'H1': 10,
        'M15': 8,
        'M5': 7,
    }
    
    def analyze(self, pair: str, live_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform full market structure analysis.
        
        Args:
            pair: Currency pair symbol
            live_data: Live market data
            
        Returns:
            Complete structure analysis
        """
        tf_analysis = {}
        
        for tf in self.TIMEFRAMES:
            tf_analysis[tf] = self._analyze_timeframe(tf, live_data)
        
        # Calculate overall structure
        overall = self._calculate_overall_structure(tf_analysis)
        
        # Calculate live structure score
        structure_score = self._calculate_structure_score(tf_analysis)
        
        return {
            'pair': pair,
            'timeframe_analysis': tf_analysis,
            'overall_structure': overall,
            'structure_score': structure_score,
            'alignment_percentage': self._calculate_alignment(tf_analysis),
            'dominant_bias': self._get_dominant_bias(tf_analysis),
        }
    
    def _analyze_timeframe(self, timeframe: str, live_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze structure for a single timeframe.
        
        In production, this would analyze actual price data.
        """
        # Simulate structure analysis
        structures = ['HH_HL', 'LH_LL', 'CONSOLIDATION']
        structure = random.choice(structures)
        
        bias = 'BULLISH' if structure == 'HH_HL' else 'BEARISH' if structure == 'LH_LL' else 'NEUTRAL'
        
        # BOS/CHOCH detection
        bos_detected = random.random() > 0.6
        choch_detected = random.random() > 0.8
        mss_detected = random.random() > 0.9
        
        # Score for this timeframe (-100 to +100)
        if bias == 'BULLISH':
            score = random.randint(30, 100)
        elif bias == 'BEARISH':
            score = random.randint(-100, -30)
        else:
            score = random.randint(-30, 30)
        
        return {
            'timeframe': timeframe,
            'structure': structure,
            'bias': bias,
            'score': score,
            'weight': self.TF_WEIGHTS[timeframe],
            'bos': {
                'detected': bos_detected,
                'direction': bias if bos_detected else None,
            },
            'choch': {
                'detected': choch_detected,
                'direction': 'BULLISH' if random.random() > 0.5 else 'BEARISH' if choch_detected else None,
            },
            'mss': {
                'detected': mss_detected,
                'direction': bias if mss_detected else None,
            },
            'key_levels': {
                'swing_high': round(random.uniform(1.0, 1.1), 5),
                'swing_low': round(random.uniform(0.9, 1.0), 5),
            },
        }
    
    def _calculate_overall_structure(self, tf_analysis: Dict[str, Dict]) -> Dict[str, Any]:
        """Calculate overall market structure."""
        bullish_count = sum(1 for tf in tf_analysis.values() if tf['bias'] == 'BULLISH')
        bearish_count = sum(1 for tf in tf_analysis.values() if tf['bias'] == 'BEARISH')
        neutral_count = sum(1 for tf in tf_analysis.values() if tf['bias'] == 'NEUTRAL')
        
        if bullish_count > bearish_count + neutral_count:
            overall_bias = 'BULLISH'
        elif bearish_count > bullish_count + neutral_count:
            overall_bias = 'BEARISH'
        else:
            overall_bias = 'NEUTRAL'
        
        # Check for BOS on higher timeframes
        htf_bos = any(
            tf_analysis[tf]['bos']['detected']
            for tf in ['MONTHLY', 'WEEKLY', 'DAILY']
        )
        
        # Check for CHOCH
        choch_detected = any(
            tf_analysis[tf]['choch']['detected']
            for tf in tf_analysis
        )
        
        return {
            'bias': overall_bias,
            'bullish_tfs': bullish_count,
            'bearish_tfs': bearish_count,
            'neutral_tfs': neutral_count,
            'htf_bos': htf_bos,
            'choch_warning': choch_detected,
            'verdict': self._get_structure_verdict(overall_bias, bullish_count, bearish_count),
        }
    
    def _calculate_structure_score(self, tf_analysis: Dict[str, Dict]) -> Dict[str, Any]:
        """
        Calculate weighted structure score (0-100).
        """
        weighted_sum = 0
        total_weight = 0
        
        for tf, analysis in tf_analysis.items():
            weight = self.TF_WEIGHTS[tf]
            # Convert -100 to +100 score to 0-100
            normalized_score = (analysis['score'] + 100) / 2
            weighted_sum += normalized_score * weight
            total_weight += weight
        
        final_score = weighted_sum / total_weight if total_weight > 0 else 50
        
        return {
            'score': round(final_score, 1),
            'interpretation': self._interpret_score(final_score),
            'tradeable': final_score >= 50 or final_score <= 50,  # Either direction
        }
    
    def _calculate_alignment(self, tf_analysis: Dict[str, Dict]) -> Dict[str, Any]:
        """Calculate timeframe alignment percentage."""
        biases = [tf['bias'] for tf in tf_analysis.values()]
        
        bullish_pct = biases.count('BULLISH') / len(biases) * 100
        bearish_pct = biases.count('BEARISH') / len(biases) * 100
        
        max_alignment = max(bullish_pct, bearish_pct)
        aligned_direction = 'BULLISH' if bullish_pct > bearish_pct else 'BEARISH'
        
        return {
            'percentage': round(max_alignment, 1),
            'direction': aligned_direction,
            'aligned_count': max(biases.count('BULLISH'), biases.count('BEARISH')),
            'total_count': len(biases),
            'is_strong': max_alignment >= 71,  # 5/7 or more
        }
    
    def _get_dominant_bias(self, tf_analysis: Dict[str, Dict]) -> str:
        """Get the dominant market bias."""
        # Weight higher timeframes more
        weighted_bias = 0
        
        for tf, analysis in tf_analysis.items():
            weight = self.TF_WEIGHTS[tf]
            if analysis['bias'] == 'BULLISH':
                weighted_bias += weight
            elif analysis['bias'] == 'BEARISH':
                weighted_bias -= weight
        
        if weighted_bias > 20:
            return 'BULLISH'
        elif weighted_bias < -20:
            return 'BEARISH'
        return 'NEUTRAL'
    
    def _get_structure_verdict(self, bias: str, bullish: int, bearish: int) -> str:
        """Get structure verdict."""
        if bias == 'BULLISH' and bullish >= 5:
            return 'STRONG BULLISH'
        elif bias == 'BULLISH':
            return 'BULLISH'
        elif bias == 'BEARISH' and bearish >= 5:
            return 'STRONG BEARISH'
        elif bias == 'BEARISH':
            return 'BEARISH'
        return 'NEUTRAL'
    
    def _interpret_score(self, score: float) -> str:
        """Interpret the structure score."""
        if score >= 85:
            return 'STRONG INSTITUTIONAL BUY'
        elif score >= 70:
            return 'MODERATE BUY'
        elif score >= 50:
            return 'SLIGHT BULLISH'
        elif score >= 30:
            return 'SLIGHT BEARISH'
        elif score >= 15:
            return 'MODERATE SELL'
        return 'STRONG INSTITUTIONAL SELL'
