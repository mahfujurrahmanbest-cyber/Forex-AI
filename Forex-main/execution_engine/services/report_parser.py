"""Weekly Report PDF Parser Service."""
import re
from datetime import datetime
from typing import Dict, Any, Optional


class WeeklyReportParser:
    """
    Parse Weekly Forex Research Report PDF.
    
    Extracts all institutional bias data, trade levels,
    and analysis from the weekly report.
    """
    
    def __init__(self):
        self.extracted_data = {}
    
    def parse_report(self, filepath: str) -> Dict[str, Any]:
        """
        Parse the weekly report PDF and extract all relevant data.
        
        Args:
            filepath: Path to the PDF file
            
        Returns:
            Dictionary containing all extracted data
        """
        try:
            # Try to use PyPDF2 or pdfplumber if available
            text = self._extract_text(filepath)
            
            return {
                'parsed': True,
                'filepath': filepath,
                'extraction_time': datetime.utcnow().isoformat(),
                
                # Scores
                'weekly_buy_score': self._extract_score(text, 'buy'),
                'weekly_sell_score': self._extract_score(text, 'sell'),
                'weekly_confidence': self._extract_confidence(text),
                'weekly_direction': self._extract_direction(text),
                'mtf_score': self._extract_mtf_score(text),
                'trade_quality_score': self._extract_trade_quality(text),
                'institutional_grade': self._extract_grade(text),
                'trade_of_week': self._extract_trade_of_week(text),
                
                # ICT Levels
                'order_blocks': self._extract_order_blocks(text),
                'fair_value_gaps': self._extract_fvg(text),
                'support_levels': self._extract_supports(text),
                'resistance_levels': self._extract_resistances(text),
                'pivot_levels': self._extract_pivots(text),
                
                # Bias Data
                'cot_bias': self._extract_cot_bias(text),
                'marketmilk_bias': self._extract_mm_bias(text),
                'dxy_bias': self._extract_dxy_bias(text),
                
                # Indicators
                'rsi': self._extract_indicator(text, 'RSI'),
                'macd': self._extract_indicator(text, 'MACD'),
                'adx': self._extract_indicator(text, 'ADX'),
                
                # Structure
                'bos': self._extract_structure(text, 'BOS'),
                'choch': self._extract_structure(text, 'CHOCH'),
                'smt': self._extract_smt(text),
                
                # Events
                'pending_news': self._extract_news_events(text),
                'weekly_strategy': self._extract_strategy(text),
                
                # Classification
                'classification': self._classify_trade(text),
            }
        except Exception as e:
            return {
                'parsed': False,
                'error': str(e),
                'filepath': filepath,
            }
    
    def _extract_text(self, filepath: str) -> str:
        """Extract text from PDF file."""
        try:
            import PyPDF2
            with open(filepath, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                text = ''
                for page in reader.pages:
                    text += page.extract_text() or ''
                return text
        except ImportError:
            # Fallback: return empty string if PyPDF2 not available
            return ''
        except Exception:
            return ''
    
    def _extract_score(self, text: str, direction: str) -> Optional[int]:
        """Extract buy or sell score from text."""
        patterns = [
            rf'{direction}\s*score[:\s]*(\d+)',
            rf'{direction}[:\s]*(\d+)/\d+',
            rf'score.*{direction}[:\s]*(\d+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return int(match.group(1))
        return None
    
    def _extract_confidence(self, text: str) -> Optional[int]:
        """Extract confidence percentage."""
        patterns = [
            r'confidence[:\s]*(\d+)%',
            r'(\d+)%\s*confidence',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return int(match.group(1))
        return None
    
    def _extract_direction(self, text: str) -> Optional[str]:
        """Extract weekly direction."""
        if re.search(r'direction[:\s]*buy', text, re.IGNORECASE):
            return 'BUY'
        elif re.search(r'direction[:\s]*sell', text, re.IGNORECASE):
            return 'SELL'
        elif re.search(r'strong\s*buy', text, re.IGNORECASE):
            return 'BUY'
        elif re.search(r'strong\s*sell', text, re.IGNORECASE):
            return 'SELL'
        return None
    
    def _extract_mtf_score(self, text: str) -> Optional[int]:
        """Extract MTF score."""
        match = re.search(r'mtf[:\s]*(\d+)', text, re.IGNORECASE)
        if match:
            return int(match.group(1))
        return None
    
    def _extract_trade_quality(self, text: str) -> Optional[int]:
        """Extract trade quality score."""
        match = re.search(r'quality[:\s]*(\d+)', text, re.IGNORECASE)
        if match:
            return int(match.group(1))
        return None
    
    def _extract_grade(self, text: str) -> Optional[str]:
        """Extract institutional grade."""
        grades = ['5 STAR', '4 STAR', '3 STAR', '2 STAR', '1 STAR',
                  'ELITE', 'HIGH', 'MODERATE', 'WEAK']
        for grade in grades:
            if grade.lower() in text.lower():
                return grade
        return None
    
    def _extract_trade_of_week(self, text: str) -> bool:
        """Check if marked as trade of the week."""
        return bool(re.search(r'trade\s*of\s*(the)?\s*week', text, re.IGNORECASE))
    
    def _extract_order_blocks(self, text: str) -> Dict[str, Any]:
        """Extract order block levels."""
        return {
            'bullish': self._find_levels(text, r'bullish\s*ob[:\s]*([\d.]+)'),
            'bearish': self._find_levels(text, r'bearish\s*ob[:\s]*([\d.]+)'),
        }
    
    def _extract_fvg(self, text: str) -> Dict[str, Any]:
        """Extract fair value gap levels."""
        return {
            'bullish': self._find_levels(text, r'bullish\s*fvg[:\s]*([\d.]+)'),
            'bearish': self._find_levels(text, r'bearish\s*fvg[:\s]*([\d.]+)'),
        }
    
    def _extract_supports(self, text: str) -> list:
        """Extract support levels."""
        return self._find_levels(text, r's[123][:\s]*([\d.]+)')
    
    def _extract_resistances(self, text: str) -> list:
        """Extract resistance levels."""
        return self._find_levels(text, r'r[123][:\s]*([\d.]+)')
    
    def _extract_pivots(self, text: str) -> Dict[str, float]:
        """Extract pivot point levels."""
        pivots = {}
        for level in ['S3', 'S2', 'S1', 'P', 'R1', 'R2', 'R3']:
            match = re.search(rf'{level}[:\s]*([\d.]+)', text, re.IGNORECASE)
            if match:
                pivots[level] = float(match.group(1))
        return pivots
    
    def _extract_cot_bias(self, text: str) -> Optional[str]:
        """Extract COT bias."""
        if re.search(r'cot.*bullish', text, re.IGNORECASE):
            return 'BULLISH'
        elif re.search(r'cot.*bearish', text, re.IGNORECASE):
            return 'BEARISH'
        return 'NEUTRAL'
    
    def _extract_mm_bias(self, text: str) -> Optional[str]:
        """Extract MarketMilk bias."""
        if re.search(r'(marketmilk|mm).*buy', text, re.IGNORECASE):
            return 'BUY'
        elif re.search(r'(marketmilk|mm).*sell', text, re.IGNORECASE):
            return 'SELL'
        return 'NEUTRAL'
    
    def _extract_dxy_bias(self, text: str) -> Optional[str]:
        """Extract DXY bias."""
        if re.search(r'dxy.*bullish|strong\s*dollar', text, re.IGNORECASE):
            return 'BULLISH'
        elif re.search(r'dxy.*bearish|weak\s*dollar', text, re.IGNORECASE):
            return 'BEARISH'
        return 'NEUTRAL'
    
    def _extract_indicator(self, text: str, indicator: str) -> Dict[str, Any]:
        """Extract indicator value and signal."""
        value_match = re.search(rf'{indicator}[:\s]*([\d.]+)', text, re.IGNORECASE)
        return {
            'value': float(value_match.group(1)) if value_match else None,
            'signal': self._get_indicator_signal(text, indicator),
        }
    
    def _get_indicator_signal(self, text: str, indicator: str) -> Optional[str]:
        """Get signal for an indicator."""
        if re.search(rf'{indicator}.*bullish', text, re.IGNORECASE):
            return 'BULLISH'
        elif re.search(rf'{indicator}.*bearish', text, re.IGNORECASE):
            return 'BEARISH'
        return 'NEUTRAL'
    
    def _extract_structure(self, text: str, structure_type: str) -> Dict[str, Any]:
        """Extract market structure signals."""
        return {
            'detected': bool(re.search(rf'{structure_type}', text, re.IGNORECASE)),
            'direction': 'BULLISH' if re.search(rf'bullish.*{structure_type}', text, re.IGNORECASE) else
                        'BEARISH' if re.search(rf'bearish.*{structure_type}', text, re.IGNORECASE) else None,
        }
    
    def _extract_smt(self, text: str) -> Dict[str, Any]:
        """Extract SMT divergence data."""
        return {
            'detected': bool(re.search(r'smt', text, re.IGNORECASE)),
            'type': 'BULLISH' if re.search(r'bullish\s*smt', text, re.IGNORECASE) else
                   'BEARISH' if re.search(r'bearish\s*smt', text, re.IGNORECASE) else None,
        }
    
    def _extract_news_events(self, text: str) -> list:
        """Extract pending news events."""
        events = []
        # Look for common high-impact events
        event_keywords = ['FOMC', 'NFP', 'CPI', 'PPI', 'GDP', 'ECB', 'BOE', 'BOJ', 'RBA']
        for keyword in event_keywords:
            if keyword.lower() in text.lower():
                events.append(keyword)
        return events
    
    def _extract_strategy(self, text: str) -> Optional[str]:
        """Extract weekly strategy."""
        strategies = [
            'TRADE AGGRESSIVELY',
            'TRADE SELECTIVELY',
            'WAIT FOR SETUPS',
            'AVOID MARKET',
        ]
        for strategy in strategies:
            if strategy.lower() in text.lower():
                return strategy
        return None
    
    def _classify_trade(self, text: str) -> str:
        """Classify the trade based on report content."""
        if re.search(r'sure\s*trade', text, re.IGNORECASE):
            return 'SURE_TRADE'
        elif re.search(r'high\s*trade', text, re.IGNORECASE):
            return 'HIGH_TRADE'
        elif re.search(r'approved', text, re.IGNORECASE):
            return 'APPROVED'
        elif re.search(r'watchlist', text, re.IGNORECASE):
            return 'WATCHLIST'
        elif re.search(r'rejected', text, re.IGNORECASE):
            return 'REJECTED'
        return 'UNKNOWN'
    
    def _find_levels(self, text: str, pattern: str) -> list:
        """Find all price levels matching a pattern."""
        matches = re.findall(pattern, text, re.IGNORECASE)
        return [float(m) for m in matches]
