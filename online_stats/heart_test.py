import requests
import time

import requests
import base64
import json
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding as crypto_padding

AES_KEY = b'OnlineStats_2026'  # 必须和服务端一致，16字节

def encrypt_payload(data: dict) -> str:
    iv = os.urandom(16)
    plaintext = json.dumps(data, ensure_ascii=False).encode('utf-8')
    padder = crypto_padding.PKCS7(128).padder()
    padded = padder.update(plaintext) + padder.finalize()
    cipher = Cipher(algorithms.AES(AES_KEY), modes.CBC(iv))
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded) + encryptor.finalize()
    return base64.b64encode(iv + ciphertext).decode('utf-8')

def heartbeat(product_key, computer_code, phone_codes):
    payload = encrypt_payload({
        "product_key":   product_key,
        "computer_code": computer_code,
        "phone_codes":   phone_codes,   # 列表，支持批量
    })
    resp = requests.post(
        "http://123.57.93.159:5003/api/v1/heartbeat",
        json={"payload": payload},
        timeout=10
    )
    return resp.json()

# 每 5 分钟上报一次
for i in range(1000):
    try:
        result = heartbeat("pk_b619a1cee85198eb2a2bc07546c1b307", f"COMP-{i+1000}", ["PHONE-001", "PHONE-002", "PHONE-003"])
        print(result)
        time.sleep(0.01)
    except Exception as e:
        print(f"崩溃----》{e}")