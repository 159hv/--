# 政企智能舆情分析系统

## 项目概览
一个基于 Flask 的政企舆情采集与管理系统，提供登录与权限控制、数据采集（百度搜索与新华网）、采集规则库、数据仓库管理、AI 引擎配置等功能，并内置 REST API 与基础后台页面。

## 技术栈
- Python 3.8+
- Flask、Flask-Login、Flask-SQLAlchemy、Flask-Migrate、Flask-RESTful、Flask-CORS
- 数据库：默认 SQLite，可配置 `DATABASE_URL`
- 前端：Jinja2 模板、Layui、jQuery
- 日志：轮转文件日志配置

## 目录结构
```
app/
├── api/                 API 路由与资源
├── models/              数据模型（用户、规则、仓库等）
├── services/            业务服务（爬虫等）
├── views/               视图与后台页面路由
└── config.py            环境配置
migrations/              数据库迁移（Alembic）
requirements/            依赖清单（base/dev/production）
static/                  静态资源（Layui、jQuery 等）
templates/               页面模板（首页、登录、管理页等）
run.py                   应用入口与初始化命令
README.md                项目说明
```

## 核心功能
- 登录与权限控制：支持管理员与普通用户，`admin_required` 装饰器限制后台访问（见 `app/views/main.py:15`）。
- 用户管理：增删改查、分页与搜索（见 `app/views/main.py:73`、`app/api/routes.py:135`）。
- 系统设置：应用名等基础配置管理（见 `app/views/main.py:168`）。
- 数据采集：
  - 百度搜索采集（关键词、分页）（见 `app/services/spider.py:9`、`app/views/main.py:210`）。
  - 新华网四川要闻采集（见 `app/services/spider.py:215`、`app/views/main.py:238`）。
  - 深度采集与自动规则更新（XPath）（见 `app/views/main.py:613`）。
- 数据仓库管理：分页、搜索、增删改、批量操作与详细内容查看（见 `app/views/main.py:446`）。
- 采集规则库：站点规则的增删改查与请求头配置（见 `app/views/main.py:1217`）。
- AI 引擎管理：配置第三方模型与凭据占位（见 `app/views/main.py:1067`）。
- REST API：舆情与用户相关接口（见 `app/api/routes.py:17`、`app/api/routes.py:135`）。

## 快速开始
1. 克隆代码：`git clone <your-repo-url>`
2. 创建虚拟环境并安装依赖：
   - 基础依赖：`pip install -r requirements/base.txt`
   - 开发依赖（可选）：`pip install -r requirements/dev.txt`
3. 初始化数据库：
   - 直接运行：`python run.py`（启动前会创建表并准备默认数据）
   - 或使用 CLI：
     - 设置环境：`set FLASK_APP=run.py`
     - 初始化命令：`flask initdb`
4. 启动服务：`python run.py`
   - 访问：`http://localhost:5000`
   - 首次登录：默认管理员 `admin/admin123`（建议登录后立刻修改密码）

## 环境变量
- `FLASK_CONFIG`（默认 `development`）：`development`/`testing`/`production`
- `FLASK_PORT`（默认 `5000`）
- `FLASK_DEBUG`（默认 `True`）
- `DATABASE_URL`、`DEV_DATABASE_URL`：数据库连接串（默认 SQLite）
- `SECRET_KEY`、`SECURITY_PASSWORD_SALT`
- `REDIS_URL`、`CELERY_BROKER_URL`、`CELERY_RESULT_BACKEND`
- 日志相关：`LOG_FOLDER`、`LOG_FILE`、`LOG_LEVEL` 等

## 数据库迁移（Flask-Migrate/Alembic）
在设置好 `FLASK_APP=run.py` 后：
- 初始化（若未存在）：`flask db init`
- 生成迁移：`flask db migrate -m "init"`
- 应用迁移：`flask db upgrade`

## API 概览
- `GET /api/topics`、`POST /api/topics`、`GET/PUT/DELETE /api/topics/<id>`
- `GET /api/keywords`
- 管理员用户接口：`GET/POST /api/v1/users`、`PUT/DELETE /api/v1/users/<id>`

## 前端页面
- 登录：`/login`
- 首页与仪表盘：`/`
- 用户管理：`/admin/users`
- 系统设置：`/admin/settings`
- AI 引擎管理：`/admin/ai-engines`
- 数据采集：`/data/collection`
- 数据仓库：`/data/warehouse`

## 开发与调试
- 入口与启动：见 `run.py:126`，支持环境变量配置与日志打印。
- 应用工厂与扩展初始化：见 `app/__init__.py:24`。
- 配置分环境：见 `app/config.py:58`、`app/config.py:78`。

## 许可
未明确指定许可证，如需开源请补充 `LICENSE` 并在此处说明。
