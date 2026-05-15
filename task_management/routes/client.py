import random
import re
from datetime import datetime, timedelta
from functools import wraps

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, current_user

from models import db, ClientAccount, Task, VerificationCode

client_bp = Blueprint('client', __name__)

_PHONE_RE = re.compile(r'^1[3-9]\d{9}$')
_CODE_RE = re.compile(r'^\d{6}$')


def client_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.is_admin:
            return redirect(url_for('client.login'))
        return f(*args, **kwargs)
    return decorated


# ── Root ──────────────────────────────────────────────────────────────────────

@client_bp.route('/')
def index():
    if current_user.is_authenticated and not current_user.is_admin:
        return redirect(url_for('client.tasks'))
    return redirect(url_for('client.login'))


# ── Auth ──────────────────────────────────────────────────────────────────────

@client_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated and not current_user.is_admin:
        return redirect(url_for('client.tasks'))

    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user = ClientAccount.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('client.tasks'))
        error = '用户名或密码错误'

    return render_template('client/login.html', error=error)


@client_bp.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')

        if not username or not password:
            error = '用户名和密码不能为空'
        elif len(password) < 6:
            error = '密码至少 6 位'
        elif password != confirm:
            error = '两次密码不一致'
        elif ClientAccount.query.filter_by(username=username).first():
            error = '用户名已存在'
        else:
            user = ClientAccount(username=username)
            user.set_password(password)
            user.ensure_api_key()
            db.session.add(user)
            db.session.commit()
            flash('注册成功，请登录', 'success')
            return redirect(url_for('client.login'))

    return render_template('client/register.html', error=error)


@client_bp.route('/logout')
@client_required
def logout():
    logout_user()
    return redirect(url_for('client.login'))


# ── Tasks ─────────────────────────────────────────────────────────────────────

@client_bp.route('/tasks')
@client_required
def tasks():
    task_list = (
        Task.query
        .filter_by(account_id=current_user.id)
        .order_by(Task.created_at.desc())
        .all()
    )
    return render_template('client/tasks.html', tasks=task_list)


@client_bp.route('/add_phone')
@client_required
def add_phone():
    return render_template('client/add_phone.html')


# ── JSON API ──────────────────────────────────────────────────────────────────

@client_bp.route('/api/send_code', methods=['POST'])
@client_required
def send_code():
    data = request.get_json(silent=True) or {}
    phone = data.get('phone', '').strip()

    if not _PHONE_RE.match(phone):
        return jsonify(success=False, message='手机号格式不正确')

    code = str(random.randint(100000, 999999))
    expires_at = datetime.utcnow() + timedelta(seconds=120)

    # Invalidate previous unused codes
    VerificationCode.query.filter_by(
        phone=phone, account_id=current_user.id, used=False
    ).update({'used': True})

    vc = VerificationCode(
        phone=phone,
        code=code,
        account_id=current_user.id,
        expires_at=expires_at,
    )
    db.session.add(vc)
    db.session.commit()

    # In production: send SMS via gateway
    print(f'[DEMO] 验证码  phone={phone}  code={code}')

    return jsonify(success=True, message='验证码已发送', demo_code=code)


@client_bp.route('/api/verify_code', methods=['POST'])
@client_required
def verify_code():
    data = request.get_json(silent=True) or {}
    phone = data.get('phone', '').strip()
    code = data.get('code', '').strip()

    if not _PHONE_RE.match(phone):
        return jsonify(success=False, message='手机号格式不正确')
    if not _CODE_RE.match(code):
        return jsonify(success=False, message='验证码必须是 6 位数字')

    vc = (
        VerificationCode.query
        .filter_by(phone=phone, code=code, account_id=current_user.id, used=False)
        .order_by(VerificationCode.created_at.desc())
        .first()
    )
    if not vc:
        return jsonify(success=False, message='验证码错误')
    if datetime.utcnow() > vc.expires_at:
        return jsonify(success=False, message='验证码已过期，请重新发送')

    vc.used = True
    task = Task(phone=phone, account_id=current_user.id, status='pending')
    db.session.add(task)
    db.session.commit()

    return jsonify(success=True, message='验证成功，任务已创建')
