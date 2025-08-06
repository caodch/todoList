# 任务管理系统

一个基于 Flask 的任务管理系统，支持任务添加、完成、删除以及图片上传功能。

## 功能特性

- [x] 添加、完成、删除任务
- [x] 任务分类管理
- [x] 图片上传（支持文件上传和粘贴截图）
- [x] 响应式设计，支持移动端
- [x] 时间显示使用北京时间
- [x] AJAX 无刷新操作
- [x] 拖拽上传图片
- [x] 任务排序功能

## 本地运行

1. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

2. 运行应用：
   ```bash
   python web.py
   ```

3. 访问地址：http://localhost:5002

## 数据库配置

应用默认使用 SQLite 数据库，数据库文件为 `todos.db`。

如需使用其他数据库，可以通过设置 `DATABASE_URL` 环境变量来配置：

### SQLite（默认）
```bash
export DATABASE_URL=sqlite:///todos.db
```

### MySQL
```bash
export DATABASE_URL=mysql://username:password@localhost:3306/database_name
```

需要安装额外依赖：
```bash
pip install PyMySQL
```

### PostgreSQL
```bash
export DATABASE_URL=postgresql://username:password@localhost:5432/database_name
```

需要安装额外依赖：
```bash
pip install psycopg2
```

## 部署方式

### 1. Vercel 部署（推荐）

1. 将代码推送到 GitHub 仓库
2. 注册 [Vercel](https://vercel.com/) 账户
3. 连接 GitHub 账户并导入项目
4. Vercel 会自动配置并部署应用

### 2. Render 部署

1. 将代码推送到 GitHub 仓库
2. 注册 [Render](https://render.com/) 账户
3. 创建 Web Service 并连接 GitHub 仓库
4. 配置如下：
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python web.py`
   - Environment Variables:
     - `PYTHON_VERSION` = `3.9.16`

### 3. Railway 部署

1. 将代码推送到 GitHub 仓库
2. 注册 [Railway](https://railway.app/) 账户
3. 创建新项目并连接 GitHub 仓库
4. Railway 会自动检测并配置 Flask 应用

### 4. Heroku 部署

1. 安装 [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)
2. 登录 Heroku：`heroku login`
3. 创建应用：`heroku create your-app-name`
4. 部署：`git push heroku master`
5. 查看应用：`heroku open`

### 5. 国内云服务器部署

1. 购买云服务器（阿里云、腾讯云等）
2. 安装 Python 环境
3. 上传项目文件到服务器
4. 安装依赖：`pip install -r requirements.txt`
5. 运行应用：`python web.py`
6. 配置安全组，开放 5002 端口
7. 通过服务器公网 IP 访问应用：http://你的服务器IP:5002

## 项目结构

```
.
├── web.py              # Flask 应用主文件
├── templates/          # HTML 模板文件
├── static/             # 静态资源文件
│   └── uploads/        # 上传的图片文件
├── requirements.txt    # Python 依赖
├── runtime.txt         # Python 运行时版本
├── Procfile            # Heroku 配置文件
└── README.md           # 项目说明文件
```

## 技术栈

- Python 3.9+
- Flask
- Flask-SQLAlchemy
- SQLite（本地）/ PostgreSQL（部署时）
- HTML5, CSS3, JavaScript

## 注意事项

- 上传的图片存储在 `static/uploads/` 目录下
- 任务数据存储在 SQLite 数据库中
- 所有时间显示使用北京时间
- 删除任务时会同时删除关联的图片文件