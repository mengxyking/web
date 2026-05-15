from flask import Flask, redirect, url_for
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from config import Config
from models import db, AdminUser, AppVersion
from routes.admin import admin_bp
from routes.api import api_bp

csrf = CSRFProtect()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    csrf.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'admin.login'

    @login_manager.user_loader
    def load_user(user_id):
        return AdminUser.query.get(int(user_id))

    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp,   url_prefix='/api')
    csrf.exempt(api_bp)

    @app.route('/')
    def index():
        return redirect(url_for('admin.dashboard'))

    import os
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    with app.app_context():
        db.create_all()
        _migrate()
        _seed_admin()

    return app


def _migrate():
    """Add new columns if they don't exist yet (idempotent)."""
    from sqlalchemy import inspect, text
    inspector = inspect(db.engine)
    cols = {c['name'] for c in inspector.get_columns('admin_users')}
    with db.engine.connect() as conn:
        if 'role' not in cols:
            conn.execute(text("ALTER TABLE admin_users ADD COLUMN role VARCHAR(10) NOT NULL DEFAULT 'admin'"))
            conn.execute(text("UPDATE admin_users SET role='super' WHERE username='admin'"))
            conn.commit()
        if 'is_active' not in cols:
            conn.execute(text('ALTER TABLE admin_users ADD COLUMN is_active TINYINT(1) NOT NULL DEFAULT 1'))
            conn.commit()

    # Composite indexes for common DailyOnline query patterns
    daily_indexes = {idx['name'] for idx in inspector.get_indexes('daily_online')}
    with db.engine.connect() as conn:
        if 'ix_daily_product_date' not in daily_indexes:
            conn.execute(text('CREATE INDEX ix_daily_product_date ON daily_online (product_id, date)'))
            conn.commit()
        if 'ix_daily_comp_date' not in daily_indexes:
            conn.execute(text('CREATE INDEX ix_daily_comp_date ON daily_online (computer_device_id, date)'))
            conn.commit()

    comp_cols = {c['name'] for c in inspector.get_columns('computer_devices')}
    phone_cols = {c['name'] for c in inspector.get_columns('phone_devices')}
    with db.engine.connect() as conn:
        if 'remark' not in comp_cols:
            conn.execute(text('ALTER TABLE computer_devices ADD COLUMN remark VARCHAR(255)'))
            conn.commit()
        if 'remark' not in phone_cols:
            conn.execute(text('ALTER TABLE phone_devices ADD COLUMN remark VARCHAR(255)'))
            conn.commit()
        if 'is_active' not in comp_cols:
            conn.execute(text('ALTER TABLE computer_devices ADD COLUMN is_active TINYINT(1) NOT NULL DEFAULT 1'))
            conn.commit()
        if 'is_active' not in phone_cols:
            conn.execute(text('ALTER TABLE phone_devices ADD COLUMN is_active TINYINT(1) NOT NULL DEFAULT 1'))
            conn.commit()
        if 'expire_at' not in comp_cols:
            conn.execute(text('ALTER TABLE computer_devices ADD COLUMN expire_at DATE'))
            conn.commit()
        if 'expire_at' not in phone_cols:
            conn.execute(text('ALTER TABLE phone_devices ADD COLUMN expire_at DATE'))
            conn.commit()


def _seed_admin():
    if not AdminUser.query.filter_by(username='admin').first():
        u = AdminUser(username='admin', role='super')
        u.set_password('admin123')
        db.session.add(u)
        db.session.commit()
        print('[INFO] Default super-admin  username=admin  password=admin123')


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5003)
