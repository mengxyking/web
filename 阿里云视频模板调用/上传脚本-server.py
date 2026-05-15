from flask import Flask, request, jsonify, url_for, send_from_directory, render_template_string
import os
from werkzeug.utils import secure_filename


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
# 确保上传文件夹存在，如果不存在则创建它
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 定义一个路由用于提供文件下载
@app.route('/downloads/<filename>', methods=['GET'])
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@app.route('/upload', methods=['POST'])
def upload_file():
    # 检查请求中是否包含文件部分
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']

    # 如果用户没有选择文件（尽管Flask通常会阻止这种情况，但最好还是检查一下）
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # 获取文件名（可能需要进行一些处理来避免安全问题，如重命名文件）
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    # 生成可访问的URL（这里假设UPLOAD_FOLDER是Web可访问的）
    # 注意：在生产环境中，你可能需要配置Web服务器（如Nginx）来提供这个目录的内容
    file_url = url_for('served_file', filename=filename, _external=True)

    return jsonify({
        'message': 'File uploaded successfully',
        'file_url': file_url  # 返回的是客户端可以访问的URL路径
    }), 201


# 新增的路由，用于提供上传的文件
@app.route('/uploads/<filename>')
def served_file(filename):
    # 加入发送文件的逻辑
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    # 运行Flask服务器，监听所有IP地址的5557端口
    app.run(debug=True, host='0.0.0.0', port=5557)