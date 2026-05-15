import os
import time
import uuid
from collections import defaultdict
from datetime import date, timedelta, datetime as dt
from functools import wraps

from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, current_app, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import func
from werkzeug.utils import secure_filename

from models import db, AdminUser, Product, ComputerDevice, PhoneDevice, DailyOnline, AppVersion, ActionLog

admin_bp = Blueprint('admin', __name__)

_login_attempts: dict = defaultdict(list)


def _rate_limited(ip):
    now = time.time()
    attempts = [t for t in _login_attempts[ip] if now - t < 300]
    _login_attempts[ip] = attempts
    return len(attempts) >= 5


def super_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_super:
            abort(403)
        return f(*args, **kwargs)
    return decorated


def _accessible_products(user):
    """Return Product query scoped to what the user may see."""
    if user.is_super:
        return Product.query
    return user.assigned_products


def _check_product_access(product_id):
    """Abort 403 if current user cannot access this product (one targeted query)."""
    if current_user.is_super:
        return
    if not current_user.assigned_products.filter_by(id=product_id).first():
        abort(403)


def _today_stats(product_id=None):
    today = date.today()
    q_comp  = db.session.query(func.count(func.distinct(DailyOnline.computer_device_id)))\
                        .filter(DailyOnline.date == today)
    q_phone = db.session.query(func.count(func.distinct(DailyOnline.phone_device_id)))\
                        .filter(DailyOnline.date == today)
    if product_id:
        q_comp  = q_comp.filter(DailyOnline.product_id  == product_id)
        q_phone = q_phone.filter(DailyOnline.product_id == product_id)
    return q_comp.scalar() or 0, q_phone.scalar() or 0


# ── Auth ──────────────────────────────────────────────────────────────────────

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))

    error = None
    if request.method == 'POST':
        ip = request.remote_addr
        if _rate_limited(ip):
            error = '登录尝试次数过多，请 5 分钟后再试'
        else:
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')
            user = AdminUser.query.filter_by(username=username, is_active=True).first()
            if user and user.check_password(password):
                login_user(user, remember=False)
                _login_attempts[ip] = []
                return redirect(url_for('admin.dashboard'))
            _login_attempts[ip].append(time.time())
            error = '用户名或密码错误'

    return render_template('admin/login.html', error=error)


@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('admin.login'))


# ── Dashboard ─────────────────────────────────────────────────────────────────

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    today = date.today()

    visible = _accessible_products(current_user).all()
    visible_ids = [p.id for p in visible]

    total_products = len([p for p in visible if p.is_active])

    active_products = db.session.query(func.count(func.distinct(DailyOnline.product_id)))\
                                .filter(
                                    DailyOnline.date == today,
                                    DailyOnline.product_id.in_(visible_ids),
                                ).scalar() or 0

    q_comp  = db.session.query(func.count(func.distinct(DailyOnline.computer_device_id)))\
                        .filter(DailyOnline.date == today, DailyOnline.product_id.in_(visible_ids))
    q_phone = db.session.query(func.count(func.distinct(DailyOnline.phone_device_id)))\
                        .filter(DailyOnline.date == today, DailyOnline.product_id.in_(visible_ids))
    comp_online  = q_comp.scalar()  or 0
    phone_online = q_phone.scalar() or 0

    product_stats = []
    for p in visible:
        c, ph = _today_stats(p.id)
        product_stats.append({'product': p, 'comp_online': c, 'phone_online': ph})

    return render_template('admin/dashboard.html',
        today=today,
        total_products=total_products,
        active_products=active_products,
        comp_online=comp_online,
        phone_online=phone_online,
        product_stats=product_stats,
    )


# ── Products ──────────────────────────────────────────────────────────────────

@admin_bp.route('/products')
@login_required
def products():
    today = date.today()
    all_prods = _accessible_products(current_user).order_by(Product.created_at.desc()).all()
    rows = []
    for p in all_prods:
        c, ph = _today_stats(p.id)
        rows.append({'product': p, 'comp_online': c, 'phone_online': ph})
    return render_template('admin/products.html', rows=rows, today=today)


@admin_bp.route('/products/add', methods=['GET', 'POST'])
@login_required
@super_required
def add_product():
    error = None
    if request.method == 'POST':
        name       = request.form.get('name', '').strip()
        remark     = request.form.get('remark', '').strip()
        custom_key = request.form.get('product_key', '').strip()

        if not name:
            error = '产品名称不能为空'
        else:
            key = custom_key if custom_key else Product.generate_key()
            if Product.query.filter_by(product_key=key).first():
                error = '该 Key 已存在，请换一个或留空自动生成'
            else:
                p = Product(name=name, product_key=key, remark=remark)
                db.session.add(p)
                db.session.commit()
                flash(f'产品「{name}」添加成功', 'success')
                return redirect(url_for('admin.products'))

    return render_template('admin/add_product.html', error=error)


@admin_bp.route('/products/<int:product_id>/toggle', methods=['POST'])
@login_required
@super_required
def toggle_product(product_id):
    p = Product.query.get_or_404(product_id)
    p.is_active = not p.is_active
    db.session.commit()
    status = '启用' if p.is_active else '禁用'
    flash(f'产品「{p.name}」已{status}', 'success')
    return redirect(url_for('admin.products'))


@admin_bp.route('/products/<int:product_id>')
@login_required
def product_detail(product_id):
    _check_product_access(product_id)

    product = Product.query.get_or_404(product_id)
    today   = date.today()

    comp_online, phone_online = _today_stats(product.id)

    days = [today - timedelta(days=i) for i in range(6, -1, -1)]  # [today-6, ..., today]
    raw_rows = db.session.query(
        DailyOnline.date,
        ComputerDevice,
        func.count(func.distinct(DailyOnline.phone_device_id)).label('phone_count')
    ).join(ComputerDevice, DailyOnline.computer_device_id == ComputerDevice.id)\
     .filter(DailyOnline.product_id == product.id, DailyOnline.date >= days[0])\
     .group_by(DailyOnline.date, ComputerDevice.id)\
     .all()
    daily_comp_rows = {d: [] for d in days}
    for row in raw_rows:
        if row[0] in daily_comp_rows:
            daily_comp_rows[row[0]].append((row[1], row[2]))
    for d in days:
        daily_comp_rows[d].sort(key=lambda x: x[1], reverse=True)

    # 近 30 天每日在线趋势
    start_date = today - timedelta(days=29)
    raw = db.session.query(
        DailyOnline.date,
        func.count(func.distinct(DailyOnline.computer_device_id)).label('comp_count'),
        func.count(func.distinct(DailyOnline.phone_device_id)).label('phone_count'),
    ).filter(
        DailyOnline.product_id == product.id,
        DailyOnline.date >= start_date,
    ).group_by(DailyOnline.date).order_by(DailyOnline.date).all()

    stat_map = {r.date: (r.comp_count, r.phone_count) for r in raw}
    chart_labels, chart_comps, chart_phones = [], [], []
    for i in range(30):
        d = start_date + timedelta(days=i)
        c, p = stat_map.get(d, (0, 0))
        chart_labels.append(d.strftime('%m-%d'))
        chart_comps.append(c)
        chart_phones.append(p)

    return render_template('admin/product_detail.html',
        product=product,
        today=today,
        days=days,
        daily_comp_rows=daily_comp_rows,
        comp_online=comp_online,
        phone_online=phone_online,
        chart_labels=chart_labels,
        chart_comps=chart_comps,
        chart_phones=chart_phones,
    )


@admin_bp.route('/products/<int:product_id>/computer/<int:comp_id>')
@login_required
def computer_detail(product_id, comp_id):
    _check_product_access(product_id)

    product  = Product.query.get_or_404(product_id)
    computer = ComputerDevice.query.get_or_404(comp_id)
    today    = date.today()
    days     = [today - timedelta(days=i) for i in range(6, -1, -1)]  # [today-6, ..., today]

    raw_phones = db.session.query(
        DailyOnline.date,
        PhoneDevice
    ).join(PhoneDevice, DailyOnline.phone_device_id == PhoneDevice.id)\
     .filter(
         DailyOnline.computer_device_id == comp_id,
         DailyOnline.product_id == product_id,
         DailyOnline.date >= days[0],
     )\
     .order_by(DailyOnline.date, DailyOnline.first_seen_at.desc())\
     .all()

    daily_phones = {d: [] for d in days}
    seen = {d: set() for d in days}
    for row in raw_phones:
        d, phone = row[0], row[1]
        if d in daily_phones and phone.id not in seen[d]:
            daily_phones[d].append(phone)
            seen[d].add(phone.id)

    return render_template('admin/computer_detail.html',
        product=product,
        computer=computer,
        days=days,
        daily_phones=daily_phones,
        today=today,
    )


# ── Device Expire ─────────────────────────────────────────────────────────────

def _log_action(action, product_id, detail):
    db.session.add(ActionLog(
        admin_id=current_user.id,
        product_id=product_id,
        action=action,
        detail=detail,
    ))


def _parse_expire(form_val):
    """'YYYY-MM-DD' → date，空字符串 → None"""
    s = (form_val or '').strip()
    return dt.strptime(s, '%Y-%m-%d').date() if s else None


@admin_bp.route('/products/<int:product_id>/computer/<int:comp_id>/expire', methods=['POST'])
@login_required
def set_computer_expire(product_id, comp_id):
    _check_product_access(product_id)
    computer = ComputerDevice.query.get_or_404(comp_id)
    expire_date = _parse_expire(request.form.get('expire_at'))
    card_type   = request.form.get('card_type', '').strip()
    computer.expire_at = expire_date
    if expire_date:
        label  = f"【{card_type}】" if card_type else ''
        detail = f"设置电脑 [{computer.device_code}] 有效期{label}至 {expire_date.strftime('%Y-%m-%d')}"
    else:
        detail = f"清除电脑 [{computer.device_code}] 有效期（恢复试用期）"
    _log_action('set_computer_expire', product_id, detail)
    db.session.commit()
    return jsonify(ok=True)


@admin_bp.route('/products/<int:product_id>/computer/<int:comp_id>/phone/<int:phone_id>/expire', methods=['POST'])
@login_required
def set_phone_expire(product_id, comp_id, phone_id):
    _check_product_access(product_id)
    phone = PhoneDevice.query.filter_by(id=phone_id, computer_device_id=comp_id).first_or_404()
    expire_date = _parse_expire(request.form.get('expire_at'))
    card_type   = request.form.get('card_type', '').strip()
    phone.expire_at = expire_date
    comp_code = phone.computer_device.device_code
    if expire_date:
        label  = f"【{card_type}】" if card_type else ''
        detail = f"设置手机 [{phone.device_code}] 有效期{label}至 {expire_date.strftime('%Y-%m-%d')}（电脑：{comp_code}）"
    else:
        detail = f"清除手机 [{phone.device_code}] 有效期（恢复试用期，电脑：{comp_code}）"
    _log_action('set_phone_expire', product_id, detail)
    db.session.commit()
    return jsonify(ok=True)


@admin_bp.route('/products/<int:product_id>/computer/<int:comp_id>/phones/expire-bulk', methods=['POST'])
@login_required
def set_phones_expire_bulk(product_id, comp_id):
    _check_product_access(product_id)
    phone_ids = [int(x) for x in request.form.getlist('phone_ids') if x.isdigit()]
    if not phone_ids:
        return jsonify(ok=False, message='未选择设备'), 400
    expire_date = _parse_expire(request.form.get('expire_at'))

    # Load before bulk-update so we have device codes for the log
    phones = PhoneDevice.query.filter(
        PhoneDevice.id.in_(phone_ids),
        PhoneDevice.computer_device_id == comp_id,
    ).all()
    computer = ComputerDevice.query.get_or_404(comp_id)

    PhoneDevice.query.filter(
        PhoneDevice.id.in_(phone_ids),
        PhoneDevice.computer_device_id == comp_id,
    ).update({'expire_at': expire_date}, synchronize_session=False)

    card_type   = request.form.get('card_type', '').strip()
    phone_codes = '、'.join(p.device_code for p in phones)
    if expire_date:
        label  = f"【{card_type}】" if card_type else ''
        detail = f"批量设置 {len(phones)} 台手机有效期{label}至 {expire_date.strftime('%Y-%m-%d')}（电脑：{computer.device_code}，手机：{phone_codes}）"
    else:
        detail = f"批量清除 {len(phones)} 台手机有效期（恢复试用期，电脑：{computer.device_code}，手机：{phone_codes}）"
    _log_action('set_phone_expire_bulk', product_id, detail)
    db.session.commit()
    return jsonify(ok=True)


# ── Action Logs (super only) ──────────────────────────────────────────────────

@admin_bp.route('/action-logs')
@login_required
@super_required
def action_logs():
    page       = request.args.get('page', 1, type=int)
    product_id = request.args.get('product_id', type=int)
    admin_id   = request.args.get('admin_id',   type=int)

    q = ActionLog.query.order_by(ActionLog.created_at.desc())
    if product_id:
        q = q.filter(ActionLog.product_id == product_id)
    if admin_id:
        q = q.filter(ActionLog.admin_id == admin_id)

    logs     = q.paginate(page=page, per_page=50, error_out=False)
    products = Product.query.order_by(Product.name).all()
    admins   = AdminUser.query.order_by(AdminUser.username).all()

    return render_template('admin/action_logs.html',
        logs=logs,
        products=products,
        admins=admins,
        selected_product_id=product_id,
        selected_admin_id=admin_id,
    )


# ── Device Toggle (disable / enable) ─────────────────────────────────────────

@admin_bp.route('/products/<int:product_id>/computer/<int:comp_id>/toggle', methods=['POST'])
@login_required
def toggle_computer(product_id, comp_id):
    _check_product_access(product_id)
    computer = ComputerDevice.query.get_or_404(comp_id)
    computer.is_active = not computer.is_active
    db.session.commit()
    return jsonify(ok=True, is_active=computer.is_active)


@admin_bp.route('/products/<int:product_id>/computer/<int:comp_id>/phone/<int:phone_id>/toggle', methods=['POST'])
@login_required
def toggle_phone(product_id, comp_id, phone_id):
    _check_product_access(product_id)
    phone = PhoneDevice.query.filter_by(id=phone_id, computer_device_id=comp_id).first_or_404()
    phone.is_active = not phone.is_active
    db.session.commit()
    return jsonify(ok=True, is_active=phone.is_active)


# ── Device Remarks ────────────────────────────────────────────────────────────

@admin_bp.route('/products/<int:product_id>/computer/<int:comp_id>/remark', methods=['POST'])
@login_required
def update_computer_remark(product_id, comp_id):
    _check_product_access(product_id)
    computer = ComputerDevice.query.get_or_404(comp_id)
    computer.remark = request.form.get('remark', '').strip() or None
    db.session.commit()
    return jsonify(ok=True)


@admin_bp.route('/products/<int:product_id>/computer/<int:comp_id>/phone/<int:phone_id>/remark', methods=['POST'])
@login_required
def update_phone_remark(product_id, comp_id, phone_id):
    _check_product_access(product_id)
    phone = PhoneDevice.query.get_or_404(phone_id)
    phone.remark = request.form.get('remark', '').strip() or None
    db.session.commit()
    return jsonify(ok=True)


# ── Account Management (super only) ──────────────────────────────────────────

@admin_bp.route('/accounts')
@login_required
@super_required
def accounts():
    all_accounts = AdminUser.query.order_by(AdminUser.created_at.desc()).all()
    return render_template('admin/accounts.html', accounts=all_accounts)


@admin_bp.route('/accounts/add', methods=['GET', 'POST'])
@login_required
@super_required
def add_account():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        role     = request.form.get('role', 'admin')

        if not username:
            error = '用户名不能为空'
        elif not password or len(password) < 6:
            error = '密码不能少于 6 位'
        elif role not in ('super', 'admin'):
            error = '角色无效'
        elif AdminUser.query.filter_by(username=username).first():
            error = '用户名已存在'
        else:
            u = AdminUser(username=username, role=role)
            u.set_password(password)
            db.session.add(u)
            db.session.commit()
            flash(f'账号「{username}」创建成功', 'success')
            return redirect(url_for('admin.accounts'))

    return render_template('admin/add_account.html', error=error)


@admin_bp.route('/accounts/<int:account_id>/toggle', methods=['POST'])
@login_required
@super_required
def toggle_account(account_id):
    u = AdminUser.query.get_or_404(account_id)
    if u.id == current_user.id:
        flash('不能禁用自己的账号', 'danger')
        return redirect(url_for('admin.accounts'))
    u.is_active = not u.is_active
    db.session.commit()
    flash(f'账号「{u.username}」已{"启用" if u.is_active else "禁用"}', 'success')
    return redirect(url_for('admin.accounts'))


@admin_bp.route('/accounts/<int:account_id>/assign', methods=['GET', 'POST'])
@login_required
@super_required
def assign_products(account_id):
    u = AdminUser.query.get_or_404(account_id)
    all_products = Product.query.order_by(Product.name).all()

    if request.method == 'POST':
        selected_ids = set(int(x) for x in request.form.getlist('product_ids'))
        # rebuild assigned list
        u.assigned_products = [p for p in all_products if p.id in selected_ids]
        db.session.commit()
        flash(f'已更新「{u.username}」的产品权限', 'success')
        return redirect(url_for('admin.accounts'))

    assigned_ids = {p.id for p in u.assigned_products}
    return render_template('admin/assign_products.html',
        account=u,
        all_products=all_products,
        assigned_ids=assigned_ids,
    )


# ── Version Management (super only) ──────────────────────────────────────────

@admin_bp.route('/products/<int:product_id>/versions')
@login_required
@super_required
def versions(product_id):
    product = Product.query.get_or_404(product_id)
    vers = AppVersion.query.filter_by(product_id=product_id)\
                           .order_by(AppVersion.version_code.desc()).all()
    return render_template('admin/versions.html', product=product, versions=vers)


@admin_bp.route('/products/<int:product_id>/versions/upload', methods=['GET', 'POST'])
@login_required
@super_required
def upload_version(product_id):
    product = Product.query.get_or_404(product_id)
    error = None

    if request.method == 'POST':
        version_name = request.form.get('version_name', '').strip()
        version_code = request.form.get('version_code', '').strip()
        description  = request.form.get('description', '').strip()
        file         = request.files.get('file')

        if not version_name:
            error = '版本名称不能为空'
        elif not version_code or not version_code.isdigit():
            error = '版本号必须为正整数'
        elif not file or not file.filename:
            error = '请选择要上传的文件'
        elif AppVersion.query.filter_by(product_id=product_id, version_code=int(version_code)).first():
            error = '该版本号已存在'
        else:
            original_name = secure_filename(file.filename)
            ext = os.path.splitext(original_name)[1]
            saved_name = f"{product_id}_{version_code}_{uuid.uuid4().hex}{ext}"
            save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], saved_name)
            file.save(save_path)
            file_size = os.path.getsize(save_path)

            v = AppVersion(
                product_id=product_id,
                version_name=version_name,
                version_code=int(version_code),
                file_path=saved_name,
                file_name=original_name,
                file_size=file_size,
                description=description,
                is_active=False,
            )
            db.session.add(v)
            db.session.commit()
            flash(f'版本 {version_name} 上传成功', 'success')
            return redirect(url_for('admin.versions', product_id=product_id))

    return render_template('admin/upload_version.html', product=product, error=error)


@admin_bp.route('/products/<int:product_id>/versions/<int:version_id>/activate', methods=['POST'])
@login_required
@super_required
def activate_version(product_id, version_id):
    # 先把该产品所有版本设为非激活
    AppVersion.query.filter_by(product_id=product_id).update({'is_active': False})
    v = AppVersion.query.get_or_404(version_id)
    v.is_active = True
    db.session.commit()
    flash(f'已将 {v.version_name} 设为当前发布版本', 'success')
    return redirect(url_for('admin.versions', product_id=product_id))


@admin_bp.route('/products/<int:product_id>/versions/<int:version_id>/delete', methods=['POST'])
@login_required
@super_required
def delete_version(product_id, version_id):
    v = AppVersion.query.get_or_404(version_id)
    # 删除磁盘文件
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], v.file_path)
    if os.path.exists(file_path):
        os.remove(file_path)
    db.session.delete(v)
    db.session.commit()
    flash(f'版本 {v.version_name} 已删除', 'success')
    return redirect(url_for('admin.versions', product_id=product_id))
