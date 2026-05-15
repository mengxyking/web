from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import secrets

db = SQLAlchemy()


class AdminUser(UserMixin, db.Model):
    __tablename__ = 'admin_users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def get_id(self):
        return f'admin_{self.id}'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return True


class ClientAccount(UserMixin, db.Model):
    __tablename__ = 'client_accounts'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    api_key = db.Column(db.String(64), unique=True, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    tasks = db.relationship('Task', backref='account', lazy='dynamic')

    def get_id(self):
        return f'client_{self.id}'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def ensure_api_key(self):
        if not self.api_key:
            self.api_key = secrets.token_hex(32)
        return self.api_key

    @property
    def is_admin(self):
        return False


class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(20), nullable=False)
    status = db.Column(
        db.Enum('pending', 'processing', 'completed', 'failed'),
        default='pending',
        nullable=False
    )
    execute_phone = db.Column(db.String(20), nullable=True)
    account_id = db.Column(db.Integer, db.ForeignKey('client_accounts.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    STATUS_MAP = {
        'pending':    ('待处理', 'secondary'),
        'processing': ('处理中', 'primary'),
        'completed':  ('已完成', 'success'),
        'failed':     ('失败',   'danger'),
    }

    @property
    def status_label(self):
        return self.STATUS_MAP.get(self.status, (self.status, 'secondary'))[0]

    @property
    def status_color(self):
        return self.STATUS_MAP.get(self.status, (self.status, 'secondary'))[1]


class VerificationCode(db.Model):
    __tablename__ = 'verification_codes'

    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(20), nullable=False)
    code = db.Column(db.String(6), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('client_accounts.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)
