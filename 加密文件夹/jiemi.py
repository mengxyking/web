from cryptography.fernet import Fernet

KEY = b"6f0yj5uxf_WLUIBORs3ylmLmZVNR_L7_WzA5SCqzVGs="

def decrypt_code():
    with open("code.secret", "rb") as f:
        enc_data = f.read()

    fernet = Fernet(KEY)
    raw_code = fernet.decrypt(enc_data).decode("utf-8")

    with open("decrypted.py", "w", encoding="utf-8") as f:
        f.write(raw_code)

    print("✅ 解密成功！")

if __name__ == "__main__":
    decrypt_code()