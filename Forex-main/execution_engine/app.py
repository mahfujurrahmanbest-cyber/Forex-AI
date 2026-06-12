"""Instant Forex Execution Engine - Main Application."""
import os
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS

from execution_engine.services.report_parser import WeeklyReportParser
from execution_engine.services.live_data import LiveMarketDataService
from execution_engine.services.market_structure import MarketStructureAnalyzer
from execution_engine.services.ict_engine import ICTExecutionEngine
from execution_engine.services.dxy_engine import DXYEngine
from execution_engine.services.news_gate import NewsGateService
from execution_engine.services.kill_zone import KillZoneEngine
from execution_engine.services.scoring_engine import ScoringEngine
from execution_engine.services.position_calculator import PositionCalculator
from execution_engine.services.decision_engine import DecisionEngine
from execution_engine.services.pdf_generator import ExecutionPDFGenerator
from execution_engine.services.excel_generator import ExecutionExcelGenerator


def create_app():
    """Create Flask application."""
    app = Flask(
        __name__,
        template_folder='templates',
        static_folder='static'
    )
    
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'execution-engine-secret')
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
    app.config['OUTPUT_FOLDER'] = os.path.join(os.path.dirname(__file__), 'outputs')
    
    # Create folders
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
    
    CORS(app)
    
    # Initialize services
    report_parser = WeeklyReportParser()
    live_data_service = LiveMarketDataService()
    structure_analyzer = MarketStructureAnalyzer()
    ict_engine = ICTExecutionEngine()
    dxy_engine = DXYEngine()
    news_gate = NewsGateService()
    kill_zone = KillZoneEngine()
    scoring_engine = ScoringEngine()
    position_calculator = PositionCalculator()
    decision_engine = DecisionEngine()
    pdf_generator = ExecutionPDFGenerator()
    excel_generator = ExecutionExcelGenerator()
    
    @app.route('/')
    def index():
        """Main dashboard."""
        return render_template('execution/index.html')
    
    @app.route('/execute')
    def execute_page():
        """Trade execution page."""
        return render_template('execution/execute.html')
    
    @app.route('/history')
    def history_page():
        """Execution history page."""
        return render_template('execution/history.html')
    
    @app.route('/api/analyze', methods=['POST'])
    def analyze_trade():
        """Main analysis endpoint."""
        try:
            # Get form data
            pair = request.form.get('pair', 'XAUUSD').upper()
            direction = request.form.get('direction', 'NOT SURE').upper()
            account_size = float(request.form.get('account_size', 10000))
            max_risk = float(request.form.get('max_risk', 1.0))
            leverage = int(request.form.get('leverage', 100))
            entry_idea = request.form.get('entry_idea', 'Market')
            
            # Parse weekly report if uploaded
            report_data = None
            if 'weekly_report' in request.files:
                file = request.files['weekly_report']
                if file.filename:
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                    file.save(filepath)
                    report_data = report_parser.parse_report(filepath)
            
            # Step 2: Get live market data
            live_data = live_data_service.fetch_all_data(pair)
            
            # Step 3: Analyze market structure
            structure_analysis = structure_analyzer.analyze(pair, live_data)
            
            # Step 4: ICT execution analysis
            ict_analysis = ict_engine.analyze(pair, live_data, structure_analysis)
            
            # Step 5: Entry quality assessment
            entry_quality = ict_engine.assess_entry_quality(
                live_data, ict_analysis, report_data
            )
            
            # Step 6: DXY analysis
            dxy_analysis = dxy_engine.analyze(live_data, report_data)
            
            # Step 7: Kill zone check
            kill_zone_result = kill_zone.get_current_session()
            
            # Step 8: News gate check
            news_result = news_gate.check_news_risk(pair)
            
            # Step 9: Calculate live MTF score
            mtf_score = scoring_engine.calculate_mtf_score(structure_analysis)
            
            # Step 10: Calculate trade quality score
            trade_quality = scoring_engine.calculate_trade_quality(
                report_data, mtf_score, ict_analysis, dxy_analysis,
                kill_zone_result, news_result
            )
            
            # Step 11: Professional trader test
            pro_test = scoring_engine.professional_trader_test(
                trade_quality, ict_analysis, news_result
            )
            
            # Step 12: Calculate instant score (/28)
            instant_score = scoring_engine.calculate_instant_score(
                report_data=report_data,
                direction=direction,
                mtf_score=mtf_score,
                ict_analysis=ict_analysis,
                live_data=live_data,
                dxy_analysis=dxy_analysis,
                news_result=news_result,
                kill_zone_result=kill_zone_result
            )
            
            # Step 13: Calculate trade levels (if score >= 14)
            trade_levels = None
            if instant_score['total'] >= 14 and not news_result['blocked']:
                trade_levels = position_calculator.calculate_levels(
                    pair=pair,
                    direction=direction,
                    live_data=live_data,
                    ict_analysis=ict_analysis,
                    account_size=account_size,
                    max_risk=max_risk,
                    leverage=leverage
                )
            
            # Step 14-15: Final decision
            final_decision = decision_engine.make_decision(
                report_data=report_data,
                live_data=live_data,
                direction=direction,
                instant_score=instant_score,
                trade_quality=trade_quality,
                news_result=news_result,
                ict_analysis=ict_analysis,
                dxy_analysis=dxy_analysis,
                pro_test=pro_test
            )
            
            # Compile full analysis
            analysis_result = {
                'timestamp': datetime.utcnow().isoformat(),
                'pair': pair,
                'direction': direction,
                'account_size': account_size,
                'max_risk': max_risk,
                'leverage': leverage,
                'entry_idea': entry_idea,
                'report_summary': report_data,
                'live_data': live_data,
                'structure_analysis': structure_analysis,
                'ict_analysis': ict_analysis,
                'entry_quality': entry_quality,
                'dxy_analysis': dxy_analysis,
                'kill_zone': kill_zone_result,
                'news_gate': news_result,
                'mtf_score': mtf_score,
                'trade_quality': trade_quality,
                'pro_test': pro_test,
                'instant_score': instant_score,
                'trade_levels': trade_levels,
                'final_decision': final_decision,
            }
            
            return jsonify({
                'success': True,
                'data': analysis_result
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/generate-pdf', methods=['POST'])
    def generate_pdf():
        """Generate PDF report."""
        try:
            data = request.json
            filepath = pdf_generator.generate(data, app.config['OUTPUT_FOLDER'])
            return send_file(
                filepath,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=os.path.basename(filepath)
            )
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/generate-excel', methods=['POST'])
    def generate_excel():
        """Generate Excel dashboard."""
        try:
            data = request.json
            filepath = excel_generator.generate(data, app.config['OUTPUT_FOLDER'])
            return send_file(
                filepath,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name=os.path.basename(filepath)
            )
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/live-price/<pair>')
    def get_live_price(pair):
        """Get live price for a pair."""
        try:
            data = live_data_service.fetch_price_data(pair.upper())
            return jsonify({'success': True, 'data': data})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/session')
    def get_session():
        """Get current trading session."""
        result = kill_zone.get_current_session()
        return jsonify({'success': True, 'data': result})
    
    @app.route('/api/news/<pair>')
    def get_news(pair):
        """Get news events for a pair."""
        result = news_gate.check_news_risk(pair.upper())
        return jsonify({'success': True, 'data': result})
    
    @app.route('/health')
    def health():
        """Health check."""
        return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})
    
    return app


app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
