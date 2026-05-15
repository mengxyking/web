from flask import Flask
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import inspect, text
from config import Config
from models import db, AdminUser, ClientAccount
from routes.admin import admin_bp
from routes.client import client_bp
from routes.api import api_bp

csrf = CSRFProtect()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    csrf.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'client.login'

    @login_manager.user_loader
    def load_user(user_id):
        if user_id.startswith('admin_'):
            return AdminUser.query.get(int(user_id.split('_')[1]))
        if user_id.startswith('client_'):
            return ClientAccount.query.get(int(user_id.split('_')[1]))
        return None

    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(client_bp, url_prefix='/')
    app.register_blueprint(api_bp,    url_prefix='/api')

    csrf.exempt(client_bp)
    csrf.exempt(api_bp)

    with app.app_context():
        db.create_all()
        _migrate(app)
        _seed_admin()
        _seed_api_keys()

    return app


def _migrate(app):
    """Add api_key column if it doesn't exist (for existing databases)."""
    inspector = inspect(db.engine)
    if 'client_accounts' in inspector.get_table_names():
        cols = [c['name'] for c in inspector.get_columns('client_accounts')]
        if 'api_key' not in cols:
            with db.engine.connect() as conn:
                conn.execute(text(
                    'ALTER TABLE client_accounts ADD COLUMN api_key VARCHAR(64) UNIQUE'
                ))
                conn.commit()
            print('[INFO] Migration: added api_key column to client_accounts')


def _seed_admin():
    if not AdminUser.query.filter_by(username='admin').first():
        admin = AdminUser(username='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print('[INFO] Default admin created  username=admin  password=admin123')


def _seed_api_keys():
    """Generate API keys for accounts that don't have one."""
    accounts = ClientAccount.query.filter_by(api_key=None).all()
    if accounts:
        for acc in accounts:
            acc.ensure_api_key()
        db.session.commit()
        print(f'[INFO] Generated API keys for {len(accounts)} account(s)')


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
