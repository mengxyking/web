from cryptography.fernet import Fernet

# ===================== 必须和你启动器里的 KEY 完全一致 =====================
KEY = b"6f0yj5uxf_WLUIBORs3ylmLmZVNR_L7_WzA5SCqzVGs="
jiami_file_path = "../jiaoyou2.py"
#jiami_file_path = "testest.py"
def encrypt_code():
    # 1. 读取你未加密的业务代码（把真实代码放在 code.py 里）
    with open(jiami_file_path, "r", encoding="utf-8") as f:
        raw_code = f.read()

    # 2. 加密
    fernet = Fernet(KEY)
    enc_data = fernet.encrypt(raw_code.encode("utf-8"))

    # 3. 写入加密文件（给启动器用）
    with open("code.secret", "wb") as f:
        f.write(enc_data)

    print("✅ 加密完成！生成文件：code.secret")
    print("ℹ️ 直接把 code.secret 放到启动器同目录即可运行")

if __name__ == "__main__":
    encrypt_code()