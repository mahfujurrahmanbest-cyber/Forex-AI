"""Position Calculator Service."""
from typing import Dict, Any, Optional
import math


class PositionCalculator:
    """
    Calculate exact trade levels and position sizing.
    
    Calculates:
    - Entry price
    - Stop loss
    - Take profit levels (TP1-TP4)
    - Lot size based on risk
    - Margin required
    - Potential profit/loss
    """
    
    # Pip values for different pairs
    PIP_VALUES = {
        'XAUUSD': 0.1,      # Gold: $0.10 per pip per 0.01 lot
        'XAGUSD': 0.01,     # Silver: $0.01 per pip per 0.01 lot
        'USDJPY': 0.01,     # JPY pairs: different pip calculation
        'EURJPY': 0.01,
        'GBPJPY': 0.01,
    }
    
    # Contract sizes
    CONTRACT_SIZES = {
        'XAUUSD': 100,      # 100 oz per lot
        'XAGUSD': 5000,     # 5000 oz per lot
        'DEFAULT': 100000,  # Standard forex lot
    }
    
    def calculate_levels(self, pair: str, direction: str,
                         live_data: Dict[str, Any],
                         ict_analysis: Dict[str, Any],
                         account_size: float,
                         max_risk: float,
                         leverage: int) -> Dict[str, Any]:
        """
        Calculate all trade levels and position sizing.
        
        Args:
            pair: Currency pair
            direction: BUY or SELL
            live_data: Live market data
            ict_analysis: ICT analysis results
            account_size: Account size in USD
            max_risk: Maximum risk percentage
            leverage: Account leverage
            
        Returns:
            Complete trade levels and sizing
        """
        pair = pair.upper().replace('/', '')
        direction = direction.upper()
        
        # Get current price
        price_data = live_data.get('price_data', {})
        current_price = price_data.get('current', 0)
        
        if not current_price:
            return {'error': 'No price data available'}
        
        # Calculate entry, SL, and TPs
        levels = self._calculate_price_levels(
            pair, direction, current_price, ict_analysis, live_data
        )
        
        # Calculate position sizing
        sizing = self._calculate_position_size(
            pair, direction, current_price,
            levels['stop_loss'], account_size, max_risk, leverage
        )
        
        # Calculate potential outcomes
        outcomes = self._calculate_outcomes(
            direction, levels, sizing['lot_size'], pair
        )
        
        return {
            'pair': pair,
            'direction': direction,
            'current_price': current_price,
            'levels': levels,
            'sizing': sizing,
            'outcomes': outcomes,
            'summary': self._generate_summary(levels, sizing, outcomes),
        }
    
    def _calculate_price_levels(self, pair: str, direction: str,
                                 current_price: float,
                                 ict_analysis: Dict[str, Any],
                                 live_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate entry, stop loss, and take profit levels.
        """
        # Get ICT levels
        order_blocks = ict_analysis.get('order_blocks', {})
        zones = ict_analysis.get('zones', {})
        liquidity = ict_analysis.get('liquidity', {})
        
        # Get technical levels
        tech_data = live_data.get('technical_data', {})
        pivots = tech_data.get('pivots', {})
        
        # Determine pip size
        if pair in ['XAUUSD']:
            pip_size = 0.1
            decimals = 2
        elif pair in ['XAGUSD']:
            pip_size = 0.01
            decimals = 3
        elif 'JPY' in pair:
            pip_size = 0.01
            decimals = 3
        else:
            pip_size = 0.0001
            decimals = 5
        
        if direction == 'BUY':
            # Entry at current or slightly below
            entry = current_price
            
            # Stop loss below support/OB
            sl_distance = current_price * 0.005  # 0.5% default
            if order_blocks.get('bullish_ob_levels'):
                ob_level = min(order_blocks['bullish_ob_levels'])
                sl_distance = max(sl_distance, (current_price - ob_level) * 1.2)
            
            stop_loss = current_price - sl_distance
            
            # Take profits at resistance levels
            tp1_distance = sl_distance * 1.5  # 1:1.5 RR
            tp2_distance = sl_distance * 3.0  # 1:3 RR
            tp3_distance = sl_distance * 5.0  # 1:5 RR
            tp4_distance = sl_distance * 8.0  # 1:8 RR
            
            tp1 = current_price + tp1_distance
            tp2 = current_price + tp2_distance
            tp3 = current_price + tp3_distance
            tp4 = current_price + tp4_distance
            
        else:  # SELL
            entry = current_price
            
            # Stop loss above resistance/OB
            sl_distance = current_price * 0.005
            if order_blocks.get('bearish_ob_levels'):
                ob_level = max(order_blocks['bearish_ob_levels'])
                sl_distance = max(sl_distance, (ob_level - current_price) * 1.2)
            
            stop_loss = current_price + sl_distance
            
            # Take profits at support levels
            tp1_distance = sl_distance * 1.5
            tp2_distance = sl_distance * 3.0
            tp3_distance = sl_distance * 5.0
            tp4_distance = sl_distance * 8.0
            
            tp1 = current_price - tp1_distance
            tp2 = current_price - tp2_distance
            tp3 = current_price - tp3_distance
            tp4 = current_price - tp4_distance
        
        # Calculate distances in pips
        sl_pips = abs(entry - stop_loss) / pip_size
        tp1_pips = abs(tp1 - entry) / pip_size
        tp2_pips = abs(tp2 - entry) / pip_size
        tp3_pips = abs(tp3 - entry) / pip_size
        tp4_pips = abs(tp4 - entry) / pip_size
        
        return {
            'entry': round(entry, decimals),
            'entry_type': 'MARKET',
            'stop_loss': round(stop_loss, decimals),
            'sl_pips': round(sl_pips, 1),
            'tp1': round(tp1, decimals),
            'tp1_pips': round(tp1_pips, 1),
            'tp1_rr': '1:1.5',
            'tp2': round(tp2, decimals),
            'tp2_pips': round(tp2_pips, 1),
            'tp2_rr': '1:3',
            'tp3': round(tp3, decimals),
            'tp3_pips': round(tp3_pips, 1),
            'tp3_rr': '1:5',
            'tp4': round(tp4, decimals),
            'tp4_pips': round(tp4_pips, 1),
            'tp4_rr': '1:8',
            'risk_reward': round(tp2_pips / sl_pips, 2) if sl_pips > 0 else 0,
        }
    
    def _calculate_position_size(self, pair: str, direction: str,
                                  entry: float, stop_loss: float,
                                  account_size: float, max_risk: float,
                                  leverage: int) -> Dict[str, Any]:
        """
        Calculate position size based on risk management.
        """
        # Risk amount in USD
        risk_amount = account_size * (max_risk / 100)
        
        # Calculate pip value and distance
        sl_distance = abs(entry - stop_loss)
        
        # Get contract size
        contract_size = self.CONTRACT_SIZES.get(pair, self.CONTRACT_SIZES['DEFAULT'])
        
        # Calculate pip value per lot
        if pair == 'XAUUSD':
            pip_value_per_lot = 1.0  # $1 per pip per 0.01 lot for gold
            pip_size = 0.1
        elif pair == 'XAGUSD':
            pip_value_per_lot = 0.50  # $0.50 per pip per 0.01 lot for silver
            pip_size = 0.01
        elif 'JPY' in pair:
            pip_value_per_lot = 1000 / entry if entry > 0 else 7  # Approximate
            pip_size = 0.01
        else:
            pip_value_per_lot = 10  # $10 per pip per standard lot
            pip_size = 0.0001
        
        # Calculate pips at risk
        pips_at_risk = sl_distance / pip_size
        
        # Calculate lot size
        if pips_at_risk > 0 and pip_value_per_lot > 0:
            lot_size = risk_amount / (pips_at_risk * pip_value_per_lot)
        else:
            lot_size = 0.01
        
        # Round to 2 decimal places (0.01 lot minimum)
        lot_size = max(0.01, round(lot_size, 2))
        
        # Calculate margin required
        margin_required = (entry * contract_size * lot_size) / leverage
        
        # Calculate max loss
        max_loss = pips_at_risk * pip_value_per_lot * lot_size
        
        return {
            'lot_size': lot_size,
            'contract_size': contract_size,
            'risk_amount': round(risk_amount, 2),
            'pips_at_risk': round(pips_at_risk, 1),
            'pip_value': round(pip_value_per_lot * lot_size, 2),
            'margin_required': round(margin_required, 2),
            'max_loss': round(max_loss, 2),
            'risk_percentage': max_risk,
            'leverage': leverage,
        }
    
    def _calculate_outcomes(self, direction: str, levels: Dict[str, Any],
                            lot_size: float, pair: str) -> Dict[str, Any]:
        """
        Calculate potential profit/loss outcomes.
        """
        # Get pip value
        if pair == 'XAUUSD':
            pip_value = 1.0 * lot_size
        elif pair == 'XAGUSD':
            pip_value = 0.50 * lot_size
        else:
            pip_value = 10 * lot_size
        
        sl_pips = levels.get('sl_pips', 0)
        tp1_pips = levels.get('tp1_pips', 0)
        tp2_pips = levels.get('tp2_pips', 0)
        tp3_pips = levels.get('tp3_pips', 0)
        tp4_pips = levels.get('tp4_pips', 0)
        
        return {
            'max_loss': round(sl_pips * pip_value, 2),
            'tp1_profit': round(tp1_pips * pip_value * 0.25, 2),  # 25% position
            'tp2_profit': round(tp2_pips * pip_value * 0.25, 2),  # 25% position
            'tp3_profit': round(tp3_pips * pip_value * 0.25, 2),  # 25% position
            'tp4_profit': round(tp4_pips * pip_value * 0.25, 2),  # 25% trailing
            'total_potential': round(
                (tp1_pips * 0.25 + tp2_pips * 0.25 + tp3_pips * 0.25 + tp4_pips * 0.25) * pip_value, 2
            ),
            'partial_close_strategy': {
                'tp1': '25% - Lock in profit',
                'tp2': '25% - Secure gains',
                'tp3': '25% - Extended target',
                'tp4': '25% - Trailing stop',
            },
        }
    
    def _generate_summary(self, levels: Dict, sizing: Dict,
                          outcomes: Dict) -> Dict[str, Any]:
        """
        Generate trade summary.
        """
        return {
            'entry': levels.get('entry'),
            'stop_loss': levels.get('stop_loss'),
            'primary_target': levels.get('tp2'),  # 1:3 RR
            'lot_size': sizing.get('lot_size'),
            'risk_amount': sizing.get('risk_amount'),
            'potential_profit': outcomes.get('total_potential'),
            'risk_reward': levels.get('risk_reward'),
            'trade_type': 'SWING' if levels.get('sl_pips', 0) > 50 else 'INTRADAY',
        }
