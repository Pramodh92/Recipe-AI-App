from flask import Flask, render_template
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import logging
import time
from config import Config
from models import db

# Initialize extensions
jwt = JWTManager()
start_time = time.time()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    CORS(app)
    
    # Configure logging
    import os
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(name)s %(message)s',
        handlers=[
            logging.FileHandler('logs/app.log'),
            logging.StreamHandler()
        ]
    )
    
    # Register blueprints
    from routes.main import main_bp
    from routes.auth import auth_bp
    from routes.recipes import recipes_bp
    from routes.ai_services import ai_bp
    from routes.health import health_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(recipes_bp, url_prefix='/recipes')
    app.register_blueprint(ai_bp, url_prefix='/ai')
    app.register_blueprint(health_bp)
    
    # Create database tables
    with app.app_context():
        # Drop and recreate all tables to update schema
        db.drop_all()
        db.create_all()
        
        # Create default admin user if not exists
        from models.user import User
        admin_user = User.query.filter_by(email='admin@airecipehub.com').first()
        if not admin_user:
            admin_user = User(
                name='Admin User',
                email='admin@airecipehub.com',
                preferred_language='en'
            )
            admin_user.set_password('admin123')  # Change in production
            db.session.add(admin_user)
            db.session.commit()
            logging.info('Created default admin user')
    
    # Global error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html'), 403
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
