from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_restful import Api
from flask_login import LoginManager
import os
import logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 创建扩展实例
db = SQLAlchemy()
migrate = Migrate()
cors = CORS()
login_manager = LoginManager()
login_manager.login_view = 'main.login'
login_manager.login_message_category = 'info'


def create_app(config_name=None):
    """应用工厂函数"""
    # 获取配置名称
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'default')
    
    app = Flask(__name__, 
                template_folder=os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'templates'),
                static_folder=os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'static'))
    
    # 配置应用
    from app.config import config
    app.config.from_object(config[config_name])
    
    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app)
    login_manager.init_app(app)
    
    # 配置日志
    configure_logging(app)
    
    return app


def configure_logging(app):
    """配置应用日志系统"""
    if not app.debug and not app.testing:
        # 创建日志文件目录
        if not os.path.exists(app.config['LOG_FOLDER']):
            os.makedirs(app.config['LOG_FOLDER'])
            
        # 配置日志格式
        log_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # 设置文件日志处理器
        file_handler = RotatingFileHandler(
            app.config['LOG_FILE'],
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=10
        )
        file_handler.setFormatter(log_format)
        file_handler.setLevel(app.config['LOG_LEVEL'])
        
        # 设置控制台日志处理器
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_format)
        console_handler.setLevel(logging.INFO)
        
        # 添加日志处理器
        app.logger.addHandler(file_handler)
        app.logger.addHandler(console_handler)
        
        # 设置日志级别
        app.logger.setLevel(app.config['LOG_LEVEL'])
        app.logger.info('应用已启动')
    
    # 注册蓝图
    from app.views import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    # 初始化API
    api = Api(app, default_mediatype='application/json')
    from app.api.routes import register_routes
    register_routes(api)
    
    return app

@login_manager.user_loader
def load_user(user_id):
    """加载用户"""
    from app.models import User
    return User.query.get(int(user_id))
