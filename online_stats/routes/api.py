import base64
import json
import os

from flask import Blueprint, request, jsonify, render_template, current_app, abort, send_from_directory
from flask_login import current_user
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding as crypto_padding

from models import db, Product, ComputerDevice, PhoneDevice, DailyOnline, AppVersion
from datetime import datetime, date
from sqlalchemy import func

api_bp = Blueprint('api', __name__)


def _ok(data=None, message='success'):
    return jsonify(code=0, message=message, data=data)

def _err(code, message):
    return jsonify(code=code, message=message, data=None), code


# ── AES-128-CBC 加解密 ─────────────────────────────────────────────────────────

def _decrypt(payload: str) -> dict:
    """Base64(IV[16] + AES-CBC(JSON)) → dict"""
    key = current_app.config['HEARTBEAT_AES_KEY']
    raw = base64.b64decode(payload)
    iv, ciphertext = raw[:16], raw[16:]
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    decryptor = cipher.decryptor()
    padded = decryptor.update(ciphertext) + decryptor.finalize()
    unpadder = crypto_padding.PKCS7(128).unpadder()
    plaintext = unpadder.update(padded) + unpadder.finalize()
    return json.loads(plaintext.decode('utf-8'))


def encrypt_payload(data: dict, key: bytes) -> str:
    """供客户端参考：dict → Base64(IV[16] + AES-CBC(JSON))"""
    iv = os.urandom(16)
    plaintext = json.dumps(data, ensure_ascii=False).encode('utf-8')
    padder = crypto_padding.PKCS7(128).padder()
    padded = padder.update(plaintext) + padder.finalize()
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded) + encryptor.finalize()
    return base64.b64encode(iv + ciphertext).decode('utf-8')


# ── POST /api/v1/heartbeat ────────────────────────────────────────────────────

@api_bp.route('/v1/heartbeat', methods=['POST'])
def heartbeat():
    """
    批量上报在线心跳（加密版）。

    Body (JSON):
      payload  string  必填  AES-128-CBC 加密后的 Base64 字符串

    解密后明文结构:
      product_key   string    产品 Key
      computer_code string    电脑设备码
      phone_codes   []string  手机设备码列表（支持批量）
    """
    body = request.get_json(silent=True) or {}
    raw_payload = body.get('payload', '').strip()

    if not raw_payload:
        return _err(400, '缺少 payload 字段')

    try:
        data = _decrypt(raw_payload)
    except Exception as e:
        return _err(400, f'解密失败，请检查加密参数：{e}')

    product_key   = data.get('product_key',   '').strip()
    computer_code = data.get('computer_code', '').strip()
    phone_codes   = data.get('phone_codes',   [])

    if not product_key:
        return _err(400, 'product_key 不能为空')
    if not computer_code:
        return _err(400, 'computer_code 不能为空')
    if not phone_codes or not isinstance(phone_codes, list):
        return _err(400, 'phone_codes 不能为空，且必须是数组')

    # 过滤空值
    phone_codes = [str(p).strip() for p in phone_codes if str(p).strip()]
    if not phone_codes:
        return _err(400, 'phone_codes 中没有有效的设备码')

    product = Product.query.filter_by(product_key=product_key, is_active=True).first()
    if not product:
        return _err(404, '产品不存在或已禁用')

    now   = datetime.now()
    today = date.today()

    # 获取或创建电脑设备
    computer = ComputerDevice.query.filter_by(
        device_code=computer_code, product_id=product.id
    ).first()
    is_new_computer = False
    if not computer:
        computer = ComputerDevice(
            device_code=computer_code, product_id=product.id,
            first_seen=now, last_seen=now,
        )
        db.session.add(computer)
        db.session.flush()
        is_new_computer = True
    else:
        if not computer.is_active:
            return _err(403, '电脑设备已禁用')
        if computer.is_expired:
            return _err(403, '电脑设备授权已过期')
        computer.last_seen = now

    # 批量处理手机：一次 SELECT IN 替代 N 次 SELECT
    existing_phones = {
        p.device_code: p
        for p in PhoneDevice.query.filter(
            PhoneDevice.device_code.in_(phone_codes),
            PhoneDevice.computer_device_id == computer.id,
        ).all()
    }

    new_phones = 0
    phone_statuses = {}
    phone_objs = {}  # code -> PhoneDevice (None means skip daily record)

    for phone_code in phone_codes:
        phone = existing_phones.get(phone_code)
        if not phone:
            phone = PhoneDevice(
                device_code=phone_code,
                computer_device_id=computer.id,
                product_id=product.id,
                first_seen=now, last_seen=now,
            )
            db.session.add(phone)
            new_phones += 1
            phone_statuses[phone_code] = 'active'
        else:
            phone.last_seen = now
            if not phone.is_active:
                phone_statuses[phone_code] = 'disabled'
                phone_objs[phone_code] = None
                continue
            if phone.is_expired:
                phone_statuses[phone_code] = 'expired'
                phone_objs[phone_code] = None
                continue
            phone_statuses[phone_code] = 'active'
        phone_objs[phone_code] = phone

    # flush 一次，让新手机获得数据库 ID
    db.session.flush()

    # 批量查今日在线记录：一次 SELECT IN 替代 N 次 SELECT
    active_phones = [p for p in phone_objs.values() if p is not None]
    if active_phones:
        active_ids = [p.id for p in active_phones]
        existing_daily = {
            r.phone_device_id
            for r in DailyOnline.query.filter(
                DailyOnline.product_id == product.id,
                DailyOnline.computer_device_id == computer.id,
                DailyOnline.phone_device_id.in_(active_ids),
                DailyOnline.date == today,
            ).all()
        }
        for p in active_phones:
            if p.id not in existing_daily:
                db.session.add(DailyOnline(
                    product_id=product.id,
                    computer_device_id=computer.id,
                    phone_device_id=p.id,
                    date=today, first_seen_at=now,
                ))

    db.session.commit()

    return _ok({
        'product':          product.name,
        'date':             today.strftime('%Y-%m-%d'),
        'computer_code':    computer_code,
        'computer_status':  'active',
        'total':            len(phone_codes),
        'new_phones':       new_phones,
        'new_computer':     is_new_computer,
        'phone_statuses':   phone_statuses,
    })


# ── GET /api/v1/stats ─────────────────────────────────────────────────────────

@api_bp.route('/v1/stats', methods=['GET'])
def stats():
    today       = date.today()
    product_key = request.args.get('product_key', '').strip()

    total_computers = db.session.query(
        func.count(func.distinct(DailyOnline.computer_device_id))
    ).filter(DailyOnline.date == today)

    total_phones = db.session.query(
        func.count(func.distinct(DailyOnline.phone_device_id))
    ).filter(DailyOnline.date == today)

    if product_key:
        product = Product.query.filter_by(product_key=product_key).first()
        if not product:
            return _err(404, '产品不存在')
        total_computers = total_computers.filter(DailyOnline.product_id == product.id)
        total_phones    = total_phones.filter(DailyOnline.product_id == product.id)

    return _ok({
        'date':             today.strftime('%Y-%m-%d'),
        'computers_online': total_computers.scalar() or 0,
        'phones_online':    total_phones.scalar() or 0,
    })


@api_bp.route('/docs')
def docs():
    if not current_user.is_authenticated or not current_user.is_super:
        abort(403)
    return render_template('api_docs.html')


# ── GET /api/v1/version ───────────────────────────────────────────────────────

@api_bp.route('/v1/version', methods=['GET'])
def check_version():
    """
    检查是否有新版本。

    Query params:
      product_key   string  必填
      version_code  int     当前客户端版本号（可选，不传则直接返回最新版本）

    Response data:
      has_update    bool
      version_name  string
      version_code  int
      description   string
      file_name     string
      file_size     int     字节数
      download_url  string
    """
    product_key  = request.args.get('product_key', '').strip()
    version_code = request.args.get('version_code', '0')

    if not product_key:
        return _err(400, 'product_key 不能为空')

    try:
        current_code = int(version_code)
    except ValueError:
        return _err(400, 'version_code 必须为整数')

    product = Product.query.filter_by(product_key=product_key, is_active=True).first()
    if not product:
        return _err(404, '产品不存在或已禁用')

    latest = AppVersion.query.filter_by(product_id=product.id, is_active=True).first()
    if not latest:
        return _ok({'has_update': False})

    has_update = latest.version_code > current_code
    download_url = request.host_url.rstrip('/') + f'/api/v1/download/{latest.id}'

    return _ok({
        'has_update':   has_update,
        'version_name': latest.version_name,
        'version_code': latest.version_code,
        'description':  latest.description or '',
        'file_name':    latest.file_name,
        'file_size':    latest.file_size,
        'download_url': download_url,
    })


# ── GET /api/v1/download/<version_id> ────────────────────────────────────────

@api_bp.route('/v1/download/<int:version_id>', methods=['GET'])
def download_version(version_id):
    """下载指定版本文件。"""
    v = AppVersion.query.get_or_404(version_id)
    upload_folder = current_app.config['UPLOAD_FOLDER']
    return send_from_directory(
        upload_folder,
        v.file_path,
        as_attachment=True,
        download_name=v.file_name,
    )
