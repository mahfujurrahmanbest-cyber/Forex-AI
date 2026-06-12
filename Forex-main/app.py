"""Flask application entry point."""
import os
from flask import Flask, render_template, jsonify
from flask_cors import CORS
from flask_caching import Cache

from config import config
from backend import db, migrate
from backend.routes import api_bp

# Initialize extensions
cache = Cache()


def create_app(config_name=None):
    """Application factory."""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    
    app = Flask(
        __name__,
        template_folder='frontend/templates',
        static_folder='frontend/static'
    )
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    cache.init_app(app)
    CORS(app)
    
    # Register blueprints
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Frontend routes
    @app.route('/')
    def index():
        """Dashboard home page."""
        return render_template('index.html')
    
    @app.route('/signals')
    def signals():
        """Signals page."""
        return render_template('signals.html')
    
    @app.route('/analysis')
    def analysis():
        """Technical analysis page."""
        return render_template('analysis.html')
    
    @app.route('/reports')
    def reports():
        """Reports page."""
        return render_template('reports.html')
    
    @app.route('/health')
    def health():
        """Health check endpoint."""
        return jsonify({'status': 'healthy'})
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app


# Create application instance
app = create_app()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
