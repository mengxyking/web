from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date, timedelta
import secrets

db = SQLAlchemy()

account_products = db.Table(
    'account_products',
    db.Column('account_id', db.Integer, db.ForeignKey('admin_users.id'), primary_key=True),
    db.Column('product_id', db.Integer, db.ForeignKey('products.id'),    primary_key=True),
)


class AdminUser(UserMixin, db.Model):
    __tablename__ = 'admin_users'

    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role          = db.Column(db.String(10), default='admin', nullable=False)
    is_active     = db.Column(db.Boolean, default=True, nullable=False)
    created_at    = db.Column(db.DateTime, default=datetime.now)

    assigned_products = db.relationship('Product', secondary='account_products', lazy='dynamic')

    @property
    def is_super(self):
        return self.role == 'super'

    def set_password(self, pw):
        self.password_hash = generate_password_hash(pw)

    def check_password(self, pw):
        return check_password_hash(self.password_hash, pw)


class Product(db.Model):
    __tablename__ = 'products'

    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(100), nullable=False)
    product_key = db.Column(db.String(64), unique=True, nullable=False)
    is_active   = db.Column(db.Boolean, default=True, nullable=False)
    remark      = db.Column(db.String(255), nullable=True)
    created_at  = db.Column(db.DateTime, default=datetime.now)

    computer_devices = db.relationship('ComputerDevice', backref='product', lazy='dynamic')
    phone_devices    = db.relationship('PhoneDevice',    backref='product', lazy='dynamic')
    daily_records    = db.relationship('DailyOnline',    backref='product', lazy='dynamic')

    @staticmethod
    def generate_key():
        return 'pk_' + secrets.token_hex(16)


class ComputerDevice(db.Model):
    __tablename__ = 'computer_devices'

    id          = db.Column(db.Integer, primary_key=True)
    device_code = db.Column(db.String(128), nullable=False)
    product_id  = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    remark      = db.Column(db.String(255), nullable=True)
    is_active   = db.Column(db.Boolean, default=True, nullable=False)
    expire_at   = db.Column(db.Date, nullable=True)
    first_seen  = db.Column(db.DateTime, default=datetime.now)
    last_seen   = db.Column(db.DateTime, default=datetime.now)

    __table_args__ = (
        db.UniqueConstraint('device_code', 'product_id', name='uq_comp_product'),
    )

    phone_devices = db.relationship('PhoneDevice',  backref='computer_device', lazy='dynamic')
    daily_records = db.relationship('DailyOnline',  backref='computer_device', lazy='dynamic')

    @property
    def effective_expire_at(self):
        return self.expire_at or (self.first_seen.date() + timedelta(days=5))

    @property
    def is_expired(self):
        return date.today() > self.effective_expire_at


class PhoneDevice(db.Model):
    __tablename__ = 'phone_devices'

    id                 = db.Column(db.Integer, primary_key=True)
    device_code        = db.Column(db.String(128), nullable=False)
    computer_device_id = db.Column(db.Integer, db.ForeignKey('computer_devices.id'), nullable=False)
    product_id         = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    remark             = db.Column(db.String(255), nullable=True)
    is_active          = db.Column(db.Boolean, default=True, nullable=False)
    expire_at          = db.Column(db.Date, nullable=True)
    first_seen         = db.Column(db.DateTime, default=datetime.now)
    last_seen          = db.Column(db.DateTime, default=datetime.now)

    __table_args__ = (
        db.UniqueConstraint('device_code', 'computer_device_id', name='uq_phone_comp'),
    )

    @property
    def effective_expire_at(self):
        return self.expire_at or (self.first_seen.date() + timedelta(days=5))

    @property
    def is_expired(self):
        return date.today() > self.effective_expire_at

    daily_records = db.relationship('DailyOnline', backref='phone_device', lazy='dynamic')


class AppVersion(db.Model):
    """每个产品的版本升级包"""
    __tablename__ = 'app_versions'

    id           = db.Column(db.Integer, primary_key=True)
    product_id   = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    version_name = db.Column(db.String(50),  nullable=False)
    version_code = db.Column(db.Integer,     nullable=False)
    file_path    = db.Column(db.String(500), nullable=False)
    file_name    = db.Column(db.String(255), nullable=False)
    file_size    = db.Column(db.Integer,     nullable=True)
    description  = db.Column(db.Text,        nullable=True)
    is_active    = db.Column(db.Boolean, default=False, nullable=False)
    created_at   = db.Column(db.DateTime, default=datetime.now)

    product = db.relationship('Product', backref='versions')


class DailyOnline(db.Model):
    """每个设备组合当天唯一一条记录，用于统计当日在线数"""
    __tablename__ = 'daily_online'

    id                 = db.Column(db.Integer, primary_key=True)
    product_id         = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    computer_device_id = db.Column(db.Integer, db.ForeignKey('computer_devices.id'), nullable=False)
    phone_device_id    = db.Column(db.Integer, db.ForeignKey('phone_devices.id'), nullable=False)
    date               = db.Column(db.Date, nullable=False, index=True)
    first_seen_at      = db.Column(db.DateTime, default=datetime.now)

    __table_args__ = (
        db.UniqueConstraint(
            'product_id', 'computer_device_id', 'phone_device_id', 'date',
            name='uq_daily_online'
        ),
    )


class ActionLog(db.Model):
    """管理员对设备有效期的操作记录"""
    __tablename__ = 'action_logs'

    id         = db.Column(db.Integer, primary_key=True)
    admin_id   = db.Column(db.Integer, db.ForeignKey('admin_users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=True)
    action     = db.Column(db.String(50), nullable=False)
    detail     = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now, index=True)

    admin   = db.relationship('AdminUser', foreign_keys=[admin_id])
    product = db.relationship('Product',   foreign_keys=[product_id])
