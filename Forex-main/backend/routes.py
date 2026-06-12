"""API routes for forex signal application."""
from flask import Blueprint, jsonify, request, send_file, current_app
from datetime import datetime, timedelta
import os

from backend import db
from backend.models import CurrencyPair, PriceData, COTData, Signal, Report
from backend.services.signal_scorer import SignalScorer
from backend.services.pdf_generator import PDFReportGenerator
from backend.services.data_fetcher import DataFetcher

api_bp = Blueprint('api', __name__)


@api_bp.route('/pairs', methods=['GET'])
def get_pairs():
    """Get all currency pairs."""
    pairs = CurrencyPair.query.filter_by(is_active=True).all()
    return jsonify({
        'success': True,
        'data': [pair.to_dict() for pair in pairs]
    })


@api_bp.route('/signals', methods=['GET'])
def get_signals():
    """Get all current signals."""
    # Get filter parameters
    min_score = request.args.get('min_score', 0, type=int)
    direction = request.args.get('direction', None)
    confidence = request.args.get('confidence', None)
    
    # Build query
    query = Signal.query.filter_by(status='active')
    
    if min_score > 0:
        query = query.filter(Signal.score >= min_score)
    if direction:
        query = query.filter_by(direction=direction.upper())
    if confidence:
        query = query.filter_by(confidence=confidence.upper())
    
    # Order by score descending
    signals = query.order_by(Signal.score.desc()).all()
    
    return jsonify({
        'success': True,
        'count': len(signals),
        'data': [signal.to_dict() for signal in signals]
    })


@api_bp.route('/signals/<symbol>', methods=['GET'])
def get_signal_by_symbol(symbol):
    """Get signal for a specific currency pair."""
    # Normalize symbol
    symbol = symbol.upper().replace('-', '/')
    
    pair = CurrencyPair.query.filter_by(symbol=symbol).first()
    if not pair:
        return jsonify({'success': False, 'error': 'Pair not found'}), 404
    
    signal = Signal.query.filter_by(
        pair_id=pair.id, 
        status='active'
    ).order_by(Signal.created_at.desc()).first()
    
    if not signal:
        return jsonify({'success': False, 'error': 'No active signal for this pair'}), 404
    
    return jsonify({
        'success': True,
        'data': signal.to_dict()
    })


@api_bp.route('/signals/top', methods=['GET'])
def get_top_signals():
    """Get top N signals by score."""
    limit = request.args.get('limit', 5, type=int)
    direction = request.args.get('direction', 'SELL')
    
    signals = Signal.query.filter_by(
        status='active',
        direction=direction.upper()
    ).order_by(Signal.score.desc()).limit(limit).all()
    
    return jsonify({
        'success': True,
        'count': len(signals),
        'data': [signal.to_dict() for signal in signals]
    })


@api_bp.route('/cot', methods=['GET'])
def get_cot_data():
    """Get COT positioning data for all pairs."""
    # Get latest COT data for each pair
    pairs = CurrencyPair.query.filter_by(is_active=True).all()
    cot_data = []
    
    for pair in pairs:
        latest_cot = COTData.query.filter_by(
            pair_id=pair.id
        ).order_by(COTData.report_date.desc()).first()
        
        if latest_cot:
            data = latest_cot.to_dict()
            data['symbol'] = pair.symbol
            cot_data.append(data)
    
    return jsonify({
        'success': True,
        'count': len(cot_data),
        'data': cot_data
    })


@api_bp.route('/cot/<symbol>', methods=['GET'])
def get_cot_by_symbol(symbol):
    """Get COT data for a specific pair."""
    symbol = symbol.upper().replace('-', '/')
    
    pair = CurrencyPair.query.filter_by(symbol=symbol).first()
    if not pair:
        return jsonify({'success': False, 'error': 'Pair not found'}), 404
    
    cot = COTData.query.filter_by(
        pair_id=pair.id
    ).order_by(COTData.report_date.desc()).first()
    
    if not cot:
        return jsonify({'success': False, 'error': 'No COT data for this pair'}), 404
    
    data = cot.to_dict()
    data['symbol'] = pair.symbol
    
    return jsonify({
        'success': True,
        'data': data
    })


@api_bp.route('/technical/<symbol>', methods=['GET'])
def get_technical_analysis(symbol):
    """Get technical analysis for a specific pair."""
    symbol = symbol.upper().replace('-', '/')
    
    pair = CurrencyPair.query.filter_by(symbol=symbol).first()
    if not pair:
        return jsonify({'success': False, 'error': 'Pair not found'}), 404
    
    price_data = PriceData.query.filter_by(
        pair_id=pair.id
    ).order_by(PriceData.timestamp.desc()).first()
    
    if not price_data:
        return jsonify({'success': False, 'error': 'No price data for this pair'}), 404
    
    data = price_data.to_dict()
    data['symbol'] = pair.symbol
    
    return jsonify({
        'success': True,
        'data': data
    })


@api_bp.route('/prices', methods=['GET'])
def get_all_prices():
    """Get latest prices for all pairs."""
    pairs = CurrencyPair.query.filter_by(is_active=True).all()
    prices = []
    
    for pair in pairs:
        latest_price = PriceData.query.filter_by(
            pair_id=pair.id
        ).order_by(PriceData.timestamp.desc()).first()
        
        if latest_price:
            data = latest_price.to_dict()
            data['symbol'] = pair.symbol
            prices.append(data)
    
    return jsonify({
        'success': True,
        'count': len(prices),
        'data': prices
    })


@api_bp.route('/refresh', methods=['POST'])
def refresh_data():
    """Refresh all market data and recalculate signals."""
    try:
        # Initialize services
        fetcher = DataFetcher()
        scorer = SignalScorer()
        
        # Fetch latest data
        fetcher.fetch_all_data()
        
        # Recalculate signals
        scorer.calculate_all_signals()
        
        return jsonify({
            'success': True,
            'message': 'Data refreshed successfully',
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/report/pdf', methods=['GET'])
def generate_pdf_report():
    """Generate and download PDF report."""
    try:
        generator = PDFReportGenerator()
        
        # Generate report
        filepath = generator.generate_weekly_report()
        
        if not filepath or not os.path.exists(filepath):
            return jsonify({
                'success': False,
                'error': 'Failed to generate report'
            }), 500
        
        # Return file for download
        return send_file(
            filepath,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=os.path.basename(filepath)
        )
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/reports', methods=['GET'])
def get_reports():
    """Get list of generated reports."""
    limit = request.args.get('limit', 10, type=int)
    
    reports = Report.query.order_by(
        Report.created_at.desc()
    ).limit(limit).all()
    
    return jsonify({
        'success': True,
        'count': len(reports),
        'data': [report.to_dict() for report in reports]
    })


@api_bp.route('/dashboard', methods=['GET'])
def get_dashboard_data():
    """Get aggregated dashboard data."""
    # Get all active signals
    signals = Signal.query.filter_by(status='active').all()
    
    # Calculate statistics
    total_signals = len(signals)
    high_confidence = len([s for s in signals if s.confidence == 'HIGH'])
    medium_confidence = len([s for s in signals if s.confidence == 'MEDIUM'])
    sell_signals = len([s for s in signals if s.direction == 'SELL'])
    buy_signals = len([s for s in signals if s.direction == 'BUY'])
    
    # Get top 3 signals
    top_signals = Signal.query.filter_by(
        status='active'
    ).order_by(Signal.score.desc()).limit(3).all()
    
    # Get latest update time
    latest_price = PriceData.query.order_by(
        PriceData.timestamp.desc()
    ).first()
    
    return jsonify({
        'success': True,
        'data': {
            'statistics': {
                'total_signals': total_signals,
                'high_confidence': high_confidence,
                'medium_confidence': medium_confidence,
                'sell_signals': sell_signals,
                'buy_signals': buy_signals,
            },
            'top_signals': [s.to_dict() for s in top_signals],
            'last_updated': latest_price.timestamp.isoformat() if latest_price else None,
        }
    })


@api_bp.route('/init', methods=['POST'])
def initialize_data():
    """Initialize database with currency pairs."""
    pairs_data = [
        {'symbol': 'XAU/USD', 'name': 'Gold', 'category': 'metal'},
        {'symbol': 'XAG/USD', 'name': 'Silver', 'category': 'metal'},
        {'symbol': 'EUR/USD', 'name': 'Euro/US Dollar', 'category': 'forex'},
        {'symbol': 'GBP/USD', 'name': 'British Pound/US Dollar', 'category': 'forex'},
        {'symbol': 'USD/JPY', 'name': 'US Dollar/Japanese Yen', 'category': 'forex'},
        {'symbol': 'GBP/JPY', 'name': 'British Pound/Japanese Yen', 'category': 'forex'},
        {'symbol': 'AUD/USD', 'name': 'Australian Dollar/US Dollar', 'category': 'forex'},
        {'symbol': 'USD/CAD', 'name': 'US Dollar/Canadian Dollar', 'category': 'forex'},
        {'symbol': 'USD/CHF', 'name': 'US Dollar/Swiss Franc', 'category': 'forex'},
        {'symbol': 'EUR/JPY', 'name': 'Euro/Japanese Yen', 'category': 'forex'},
        {'symbol': 'EUR/GBP', 'name': 'Euro/British Pound', 'category': 'forex'},
        {'symbol': 'NZD/USD', 'name': 'New Zealand Dollar/US Dollar', 'category': 'forex'},
    ]
    
    created = 0
    for pair_data in pairs_data:
        existing = CurrencyPair.query.filter_by(symbol=pair_data['symbol']).first()
        if not existing:
            pair = CurrencyPair(**pair_data)
            db.session.add(pair)
            created += 1
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'Initialized {created} currency pairs',
        'total_pairs': CurrencyPair.query.count()
    })
