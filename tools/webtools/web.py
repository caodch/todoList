#!/usr/bin/env python3
# app.py
from flask import Flask, render_template, request, redirect, url_for, jsonify
import datetime
import os
import sys
import base64
from werkzeug.utils import secure_filename

# 添加导入语句以支持打包
try:
    import sqlalchemy
except ImportError:
    print("请安装SQLAlchemy: pip install SQLAlchemy")
    sys.exit(1)

try:
    import flask_sqlalchemy
except ImportError:
    print("请安装Flask-SQLAlchemy: pip install Flask-SQLAlchemy")
    sys.exit(1)

# 检查是否为打包环境
def is_frozen():
    """检查是否为PyInstaller打包环境"""
    return getattr(sys, 'frozen', False)

# 处理打包后的资源路径
def resource_path(relative_path):
    """获取资源文件路径，支持打包后运行"""
    try:
        # PyInstaller创建的临时文件夹
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

# 初始化Flask应用，显式指定静态文件夹
if is_frozen():
    # 打包环境
    static_folder = os.path.join(os.path.dirname(sys.executable), 'static')
    app = Flask(__name__, 
                template_folder=resource_path('templates'),
                static_folder=static_folder)
else:
    # 开发环境
    app = Flask(__name__, 
                template_folder=resource_path('templates'))

# 配置数据库 URI，支持多种环境
# 可以通过设置 DATABASE_URL 环境变量来配置数据库
# SQLite 示例: sqlite:///todos.db
# MySQL 示例: mysql://username:password@localhost:3306/database_name
# PostgreSQL 示例: postgresql://username:password@localhost:5432/database_name
database_url = os.environ.get('DATABASE_URL')
if database_url and database_url.startswith("postgres://"):
    # 修复 Heroku 提供的 postgres:// URL 为 postgresql://
    database_url = database_url.replace("postgres://", "postgresql://", 1)

# 如果没有设置 DATABASE_URL 环境变量，则使用默认的 SQLite 数据库
app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///todos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 配置上传文件夹
if is_frozen():
    # 打包环境 - 使用可执行文件同级目录的static文件夹
    base_dir = os.path.dirname(sys.executable)
    upload_folder = os.path.join(base_dir, 'static', 'uploads')
else:
    # 开发环境
    upload_folder = os.environ.get('UPLOAD_FOLDER') or os.path.join(os.path.abspath('.'), 'static', 'uploads')

app.config['UPLOAD_FOLDER'] = upload_folder
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 限制上传文件大小为16MB

# 确保上传文件夹存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 允许上传的文件类型
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# 初始化数据库
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_base64_image(base64_data):
    """保存base64格式的图片数据"""
    try:
        # 移除base64数据的前缀
        if 'base64,' in base64_data:
            base64_data = base64_data.split('base64,')[1]

        # 解码base64数据
        image_data = base64.b64decode(base64_data)

        # 生成文件名
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"pasted_{timestamp}.png"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        # 保存文件
        with open(file_path, 'wb') as f:
            f.write(image_data)

        # 返回相对于静态文件夹的路径
        return os.path.join('uploads', filename).replace("\\", "/")
    except Exception as e:
        print(f"保存图片时出错: {e}")
        return None

def get_beijing_time():
    """获取北京时间"""
    beijing_tz = datetime.timezone(datetime.timedelta(hours=8))
    return datetime.datetime.now(beijing_tz)

# 新增 Category 类表示任务分类
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=get_beijing_time)

    # 建立与 Todo 表的关联关系
    todos = db.relationship('Todo', backref='category', lazy=True)

    def __repr__(self):
        return f'<Category {self.name}>'

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=get_beijing_time)
    # 添加图片路径字段
    image_path = db.Column(db.String(300), nullable=True)

    # 添加外键关联到 Category 表
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)

    def __repr__(self):
        return f'<Todo {self.content}>'

@app.route('/')
def index():
    todos = Todo.query.all()
    return render_template('index.html', todos=todos)

# AJAX 添加任务接口
@app.route('/add', methods=['POST'])
def add():
    try:
        content = request.form['content']
        image_path = None

        # 处理粘贴的图片（优先处理）
        if 'pasted_image' in request.form and request.form['pasted_image']:
            pasted_image_data = request.form['pasted_image']
            image_path = save_base64_image(pasted_image_data)
        # 处理上传的图片文件（只有在没有粘贴图片时才处理）
        elif 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # 添加时间戳以避免文件名冲突，同时保留原始扩展名
                timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                name, ext = os.path.splitext(filename)
                filename = f"{timestamp}_{name}{ext}"  # 使用下划线分隔时间戳和原始文件名
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                # 保存相对于静态文件夹的路径
                image_path = os.path.join('uploads', filename).replace("\\", "/")

        new_todo = Todo(content=content, image_path=image_path)
        db.session.add(new_todo)
        db.session.commit()
        return jsonify({'success': True, 'message': '任务添加成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'添加任务失败: {str(e)}'}), 500

# AJAX 完成/取消完成任务接口
@app.route('/complete/<int:todo_id>', methods=['POST'])
def complete(todo_id):
    try:
        todo = Todo.query.get(todo_id)
        if todo:
            todo.completed = not todo.completed
            db.session.commit()
            return jsonify({'success': True, 'message': '任务状态更新成功'})
        else:
            return jsonify({'success': False, 'message': '任务不存在'}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'更新任务状态失败: {str(e)}'}), 500

# AJAX 删除任务接口
@app.route('/delete/<int:todo_id>', methods=['POST'])
def delete(todo_id):
    try:
        todo = Todo.query.get(todo_id)
        if todo:
            # 如果任务有关联的图片，删除图片文件
            if todo.image_path:
                # 获取图片文件名
                image_filename = todo.image_path.split('/')[-1]
                # 构建完整路径
                if is_frozen():
                    # 打包环境
                    image_file_path = os.path.join(os.path.dirname(sys.executable), 'static', 'uploads', image_filename)
                else:
                    # 开发环境
                    image_file_path = os.path.join(os.path.abspath('.'), 'static', 'uploads', image_filename)
                
                if os.path.exists(image_file_path):
                    os.remove(image_file_path)

            db.session.delete(todo)
            db.session.commit()
            return jsonify({'success': True, 'message': '任务删除成功'})
        else:
            return jsonify({'success': False, 'message': '任务不存在'}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'删除任务失败: {str(e)}'}), 500


if __name__ == '__main__':
    with app.app_context():
        # 只有在数据库文件不存在时才创建表
        db.create_all()
    # 获取环境变量中的端口，如果没有则使用默认端口 5002
    port = int(os.environ.get('PORT', 5002))
    # 更改 host 为 0.0.0.0 以允许外部访问
    app.run(debug=False, host='0.0.0.0', port=port)