import base64


def encrypt_and_modify(shebeima):
    """对输入的字符串进行Base64编码，并在特定位置插入字符"""
    input_text = shebeima

    if not input_text:
        return

    # 进行Base64编码
    encoded_bytes = base64.b64encode(input_text.encode('utf-8'))
    encoded_str = encoded_bytes.decode('utf-8')

    # 在特定位置插入字符
    modified_str = list(encoded_str)

    # 确保字符串足够长，以避免索引错误
    if len(modified_str) >= 1:
        modified_str[0] += 'a'
    if len(modified_str) >= 3:
        modified_str[2] += 'b'
    if len(modified_str) >= 5:
        modified_str[4] += 'f'
    if len(modified_str) >= 2:
        modified_str[-2] += 'g'

    # 将列表转换回字符串
    final_str = ''.join(modified_str)
    return final_str

print(encrypt_and_modify("c360b7b9c1b34cd608"))