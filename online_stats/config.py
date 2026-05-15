import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'online-stats-secret-xK9#mL2@pQ5!')

    DB_HOST     = os.environ.get('DB_HOST',     'localhost')
    DB_PORT     = os.environ.get('DB_PORT',     '3306')
    DB_USER     = os.environ.get('DB_USER',     'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '123456')
    DB_NAME     = os.environ.get('DB_NAME',     'online_stats')

    SQLALCHEMY_DATABASE_URI = (
        f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 7200

    # AES-128-CBC 加密密钥（16 字节），客户端与服务端共享
    HEARTBEAT_AES_KEY = os.environ.get('HEARTBEAT_AES_KEY', 'OnlineStats_2026').encode('utf-8')[:16]

    # 版本文件上传目录
    UPLOAD_FOLDER     = os.path.join(BASE_DIR, 'uploads')
    MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500 MB
