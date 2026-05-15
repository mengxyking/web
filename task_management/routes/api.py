from flask import Blueprint, request, jsonify, render_template
from models import Task, ClientAccount

api_bp = Blueprint('api', __name__)


def _ok(data):
    return jsonify(code=0, message='success', data=data)

def _err(code, message):
    return jsonify(code=code, message=message, data=None), code


# ── GET /api/v1/tasks ─────────────────────────────────────────────────────────

@api_bp.route('/v1/tasks', methods=['GET'])
def get_tasks():
    page     = request.args.get('page',     1,  type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status   = request.args.get('status',   '').strip()
    phone    = request.args.get('phone',    '').strip()

    per_page = min(max(per_page, 1), 100)
    page     = max(page, 1)

    query = Task.query.join(ClientAccount, Task.account_id == ClientAccount.id)

    if status:
        if status not in ('pending', 'processing', 'completed', 'failed'):
            return _err(400, 'status 参数无效，可选值：pending / processing / completed / failed')
        query = query.filter(Task.status == status)

    if phone:
        query = query.filter(Task.phone.like(f'%{phone}%'))

    query = query.order_by(Task.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    task_list = [
        {
            'id':            t.id,
            'phone':         t.phone,
            'status':        t.status,
            'status_label':  t.status_label,
            'execute_phone': t.execute_phone,
            'account':       t.account.username,
            'created_at':    t.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at':    t.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
        }
        for t in pagination.items
    ]

    return _ok({
        'list': task_list,
        'pagination': {
            'total':    pagination.total,
            'page':     pagination.page,
            'per_page': pagination.per_page,
            'pages':    pagination.pages,
            'has_prev': pagination.has_prev,
            'has_next': pagination.has_next,
        }
    })


# ── API docs page ─────────────────────────────────────────────────────────────

@api_bp.route('/docs')
def docs():
    return render_template('api_docs.html')
