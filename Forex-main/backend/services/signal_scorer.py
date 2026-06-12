"""Signal scoring service for forex analysis."""
from datetime import datetime
from flask import current_app

from backend import db
from backend.models import CurrencyPair, PriceData, COTData, Signal


class SignalScorer:
    """Calculate trading signals based on multiple factors."""
    
    def __init__(self):
        self.weights = {
            'cot_bearish': 2,
            'rsi_extreme': 2,
            'macd_bearish': 1,
            'below_50_ema': 1,
            'below_200_ema': 1,
            'technical_sell': 1,
            'near_resistance': 1,
            'weekly_downtrend': 1,
        }
    
    def calculate_signal_score(self, pair_id):
        """
        Calculate signal score for a currency pair.
        
        Returns:
            dict: Score breakdown and total score
        """
        # Get latest price data
        price_data = PriceData.query.filter_by(
            pair_id=pair_id
        ).order_by(PriceData.timestamp.desc()).first()
        
        # Get latest COT data
        cot_data = COTData.query.filter_by(
            pair_id=pair_id
        ).order_by(COTData.report_date.desc()).first()
        
        if not price_data:
            return None
        
        score = 0
        breakdown = {}
        
        # 1. COT Net Position bearish (+2 pts)
        if cot_data and cot_data.nc_net and cot_data.nc_net < 0:
            score += self.weights['cot_bearish']
            breakdown['cot_bearish'] = {
                'points': self.weights['cot_bearish'],
                'value': cot_data.nc_net,
                'met': True
            }
        else:
            breakdown['cot_bearish'] = {
                'points': 0,
                'value': cot_data.nc_net if cot_data else None,
                'met': False
            }
        
        # 2. RSI extreme (+2 pts) - overbought (>65) or oversold (<35)
        if price_data.rsi_14:
            if price_data.rsi_14 > 65 or price_data.rsi_14 < 35:
                score += self.weights['rsi_extreme']
                breakdown['rsi_extreme'] = {
                    'points': self.weights['rsi_extreme'],
                    'value': price_data.rsi_14,
                    'met': True
                }
            else:
                breakdown['rsi_extreme'] = {
                    'points': 0,
                    'value': price_data.rsi_14,
                    'met': False
                }
        
        # 3. MACD bearish crossover (+1 pt)
        if price_data.macd_histogram and price_data.macd_histogram < 0:
            score += self.weights['macd_bearish']
            breakdown['macd_bearish'] = {
                'points': self.weights['macd_bearish'],
                'value': price_data.macd_histogram,
                'met': True
            }
        else:
            breakdown['macd_bearish'] = {
                'points': 0,
                'value': price_data.macd_histogram,
                'met': False
            }
        
        # 4. Price below 50 EMA (+1 pt)
        current_price = price_data.bid or price_data.close_price
        if current_price and price_data.ema_50:
            if current_price < price_data.ema_50:
                score += self.weights['below_50_ema']
                breakdown['below_50_ema'] = {
                    'points': self.weights['below_50_ema'],
                    'value': f'{current_price} < {price_data.ema_50}',
                    'met': True
                }
            else:
                breakdown['below_50_ema'] = {
                    'points': 0,
                    'value': f'{current_price} >= {price_data.ema_50}',
                    'met': False
                }
        
        # 5. Price below 200 EMA (+1 pt)
        if current_price and price_data.ema_200:
            if current_price < price_data.ema_200:
                score += self.weights['below_200_ema']
                breakdown['below_200_ema'] = {
                    'points': self.weights['below_200_ema'],
                    'value': f'{current_price} < {price_data.ema_200}',
                    'met': True
                }
            else:
                breakdown['below_200_ema'] = {
                    'points': 0,
                    'value': f'{current_price} >= {price_data.ema_200}',
                    'met': False
                }
        
        # 6. Technical consensus = SELL (+1 pt)
        if price_data.ma_consensus and price_data.ma_consensus.upper() in ['SELL', 'STRONG SELL']:
            score += self.weights['technical_sell']
            breakdown['technical_sell'] = {
                'points': self.weights['technical_sell'],
                'value': price_data.ma_consensus,
                'met': True
            }
        else:
            breakdown['technical_sell'] = {
                'points': 0,
                'value': price_data.ma_consensus,
                'met': False
            }
        
        # 7. Price near resistance (+1 pt) - within 0.3%
        if current_price and price_data.resistance_1:
            distance_pct = abs(current_price - price_data.resistance_1) / price_data.resistance_1 * 100
            if distance_pct <= 0.3:
                score += self.weights['near_resistance']
                breakdown['near_resistance'] = {
                    'points': self.weights['near_resistance'],
                    'value': f'{distance_pct:.2f}% from R1',
                    'met': True
                }
            else:
                breakdown['near_resistance'] = {
                    'points': 0,
                    'value': f'{distance_pct:.2f}% from R1',
                    'met': False
                }
        
        # Determine confidence level
        if score >= 8:
            confidence = 'HIGH'
        elif score >= 5:
            confidence = 'MEDIUM'
        else:
            confidence = 'LOW'
        
        return {
            'score': score,
            'confidence': confidence,
            'breakdown': breakdown,
            'max_score': 10
        }
    
    def calculate_trade_levels(self, pair_id, direction='SELL'):
        """
        Calculate entry, stop loss, and take profit levels.
        
        Returns:
            dict: Trade levels
        """
        price_data = PriceData.query.filter_by(
            pair_id=pair_id
        ).order_by(PriceData.timestamp.desc()).first()
        
        if not price_data:
            return None
        
        current_price = price_data.bid or price_data.close_price
        
        if direction == 'SELL':
            # Entry at current price or slightly below resistance
            entry = current_price
            
            # Stop loss above resistance
            if price_data.resistance_1:
                stop_loss = price_data.resistance_1 * 1.002  # 0.2% buffer
            else:
                stop_loss = current_price * 1.01  # 1% default
            
            # Take profit at support levels
            if price_data.support_1:
                tp1 = price_data.support_1
            else:
                tp1 = current_price * 0.985  # 1.5% default
            
            if price_data.support_2:
                tp2 = price_data.support_2
            else:
                tp2 = current_price * 0.97  # 3% default
        else:  # BUY
            entry = current_price
            
            if price_data.support_1:
                stop_loss = price_data.support_1 * 0.998
            else:
                stop_loss = current_price * 0.99
            
            if price_data.resistance_1:
                tp1 = price_data.resistance_1
            else:
                tp1 = current_price * 1.015
            
            if price_data.resistance_2:
                tp2 = price_data.resistance_2
            else:
                tp2 = current_price * 1.03
        
        # Calculate risk:reward ratio
        risk = abs(entry - stop_loss)
        reward = abs(tp1 - entry)
        rr_ratio = reward / risk if risk > 0 else 0
        
        return {
            'entry': round(entry, 5),
            'stop_loss': round(stop_loss, 5),
            'take_profit_1': round(tp1, 5),
            'take_profit_2': round(tp2, 5),
            'risk_reward_ratio': round(rr_ratio, 2),
            'risk_pips': round(risk * 10000, 1) if risk < 1 else round(risk, 2),
        }
    
    def generate_analysis(self, pair_id, score_data):
        """
        Generate text analysis for a signal.
        
        Returns:
            str: Analysis text
        """
        pair = CurrencyPair.query.get(pair_id)
        if not pair:
            return ""
        
        breakdown = score_data.get('breakdown', {})
        factors = []
        
        if breakdown.get('cot_bearish', {}).get('met'):
            factors.append("institutional positioning is bearish")
        
        if breakdown.get('rsi_extreme', {}).get('met'):
            rsi_val = breakdown['rsi_extreme'].get('value')
            if rsi_val and rsi_val > 65:
                factors.append(f"RSI at {rsi_val:.1f} indicates overbought conditions")
            elif rsi_val and rsi_val < 35:
                factors.append(f"RSI at {rsi_val:.1f} shows oversold bounce exhaustion")
        
        if breakdown.get('macd_bearish', {}).get('met'):
            factors.append("MACD shows bearish momentum")
        
        if breakdown.get('technical_sell', {}).get('met'):
            factors.append("technical indicators consensus is SELL")
        
        if factors:
            analysis = f"{pair.symbol} shows a {score_data['confidence'].lower()} confidence SHORT signal. "
            analysis += "Key factors: " + ", ".join(factors) + ". "
            analysis += f"Overall score: {score_data['score']}/10."
        else:
            analysis = f"{pair.symbol} does not meet minimum criteria for a high-probability trade setup."
        
        return analysis
    
    def calculate_all_signals(self):
        """
        Calculate signals for all active currency pairs.
        
        Returns:
            list: List of generated signals
        """
        pairs = CurrencyPair.query.filter_by(is_active=True).all()
        signals = []
        
        for pair in pairs:
            # Calculate score
            score_data = self.calculate_signal_score(pair.id)
            if not score_data:
                continue
            
            # Only create signals for score >= 5
            if score_data['score'] < 5:
                continue
            
            # Calculate trade levels
            levels = self.calculate_trade_levels(pair.id, 'SELL')
            if not levels:
                continue
            
            # Generate analysis
            analysis = self.generate_analysis(pair.id, score_data)
            
            # Deactivate old signals for this pair
            Signal.query.filter_by(
                pair_id=pair.id,
                status='active'
            ).update({'status': 'replaced'})
            
            # Create new signal
            signal = Signal(
                pair_id=pair.id,
                direction='SELL',
                score=score_data['score'],
                confidence=score_data['confidence'],
                entry_price=levels['entry'],
                stop_loss=levels['stop_loss'],
                take_profit_1=levels['take_profit_1'],
                take_profit_2=levels['take_profit_2'],
                risk_reward_ratio=levels['risk_reward_ratio'],
                risk_percent=1.0,
                timeframe='H4',
                estimated_duration='3-5 days',
                score_breakdown=score_data['breakdown'],
                analysis=analysis,
                status='active'
            )
            
            db.session.add(signal)
            signals.append(signal)
        
        db.session.commit()
        return signals
