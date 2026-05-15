import time
from collections import defaultdict
from functools import wraps
from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user

from models import db, AdminUser, Task, ClientAccount

admin_bp = Blueprint('admin', __name__)

# In-memory rate limiter: ip -> [timestamp, ...]
_login_attempts: dict = defaultdict(list)


def _is_rate_limited(ip: str) -> bool:
    now = time.time()
    attempts = [t for t in _login_attempts[ip] if now - t < 300]
    _login_attempts[ip] = attempts
    return len(attempts) >= 5


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated


# ── Auth ──────────────────────────────────────────────────────────────────────

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated and current_user.is_admin:
        return redirect(url_for('admin.dashboard'))

    error = None
    if request.method == 'POST':
        ip = request.remote_addr
        if _is_rate_limited(ip):
            error = '登录尝试次数过多，请 5 分钟后再试'
        else:
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')
            user = AdminUser.query.filter_by(username=username).first()
            if user and user.check_password(password):
                login_user(user, remember=False)
                _login_attempts[ip] = []
                return redirect(url_for('admin.dashboard'))
            _login_attempts[ip].append(time.time())
            error = '用户名或密码错误'

    return render_template('admin/login.html', error=error)


@admin_bp.route('/logout')
@admin_required
def logout():
    logout_user()
    return redirect(url_for('admin.login'))


# ── Dashboard ─────────────────────────────────────────────────────────────────

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    page = request.args.get('page', 1, type=int)
    phone_filter = request.args.get('phone', '').strip()
    status_filter = request.args.get('status', '').strip()

    query = Task.query.join(ClientAccount, Task.account_id == ClientAccount.id)
    if phone_filter:
        query = query.filter(Task.phone.like(f'%{phone_filter}%'))
    if status_filter:
        query = query.filter(Task.status == status_filter)
    query = query.order_by(Task.created_at.desc())

    pagination = query.paginate(page=page, per_page=20, error_out=False)
    return render_template(
        'admin/dashboard.html',
        tasks=pagination.items,
        pagination=pagination,
        phone_filter=phone_filter,
        status_filter=status_filter,
    )


# ── Task operations ───────────────────────────────────────────────────────────

@admin_bp.route('/task/<int:task_id>/update', methods=['POST'])
@admin_required
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    new_status = request.form.get('status')
    execute_phone = request.form.get('execute_phone', '').strip()

    if new_status in ('pending', 'processing', 'completed', 'failed'):
        task.status = new_status
        task.updated_at = datetime.utcnow()
    if execute_phone:
        task.execute_phone = execute_phone

    db.session.commit()
    flash('任务已更新', 'success')
    return redirect(_back_url())


@admin_bp.route('/task/<int:task_id>/delete', methods=['POST'])
@admin_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    flash('任务已删除', 'success')
    return redirect(_back_url())


def _back_url():
    return request.referrer or url_for('admin.dashboard')
