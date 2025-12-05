import os
import json
import logging
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    """基础配置类"""
    # 应用配置
    APP_NAME = os.environ.get('APP_NAME') or '政企智能舆情分析系统'
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string-2024'
    
    # 数据库配置 - 使用SQLite作为默认数据库
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'data.sqlite')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # SQLAlchemy连接池配置
    SQLALCHEMY_POOL_SIZE = int(os.environ.get('SQLALCHEMY_POOL_SIZE') or 10)  # 连接池大小
    SQLALCHEMY_POOL_TIMEOUT = int(os.environ.get('SQLALCHEMY_POOL_TIMEOUT') or 30)  # 连接超时时间
    SQLALCHEMY_POOL_RECYCLE = int(os.environ.get('SQLALCHEMY_POOL_RECYCLE') or 3600)  # 连接回收时间
    SQLALCHEMY_MAX_OVERFLOW = int(os.environ.get('SQLALCHEMY_MAX_OVERFLOW') or 5)  # 连接池最大溢出数量
    
    # Redis配置
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    
    # Celery配置
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL') or 'redis://localhost:6379/1'
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND') or 'redis://localhost:6379/2'
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'
    
    # 日志配置
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'
    LOG_FOLDER = os.environ.get('LOG_FOLDER') or os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'logs')
    LOG_FILE = os.environ.get('LOG_FILE') or os.path.join(LOG_FOLDER, 'app.log')
    LOG_MAX_BYTES = int(os.environ.get('LOG_MAX_BYTES') or 10485760)  # 10MB
    LOG_BACKUP_COUNT = int(os.environ.get('LOG_BACKUP_COUNT') or 5)
    
    # 爬取配置
    CRAWL_INTERVAL = int(os.environ.get('CRAWL_INTERVAL') or 3600)  # 默认1小时爬取一次
    MAX_CRAWL_RESULTS = int(os.environ.get('MAX_CRAWL_RESULTS') or 100)  # 每次爬取最大结果数
    CRAWL_TIMEOUT = int(os.environ.get('CRAWL_TIMEOUT') or 30)  # 爬取超时时间
    CRAWL_RETRY_TIMES = int(os.environ.get('CRAWL_RETRY_TIMES') or 3)  # 爬取重试次数
    
    # 安全配置
    CSRF_ENABLED = True
    X_FRAME_OPTIONS = 'SAMEORIGIN'
    SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT') or 'hard-to-guess-salt-2024'
    
    # 分页配置
    PER_PAGE = int(os.environ.get('PER_PAGE') or 20)
    MAX_PER_PAGE = int(os.environ.get('MAX_PER_PAGE') or 100)

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'
    
    # 开发环境数据库配置
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'data_dev.sqlite')

class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    DEBUG = False
    
    # 测试环境使用内存数据库
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # 测试环境禁用CSRF保护
    CSRF_ENABLED = False

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    TESTING = False
    
    # 生产环境数据库配置
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'data_prod.sqlite')
    
    # 生产环境应该使用更强的密钥
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'production-secret-key-2024-very-strong'
    SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT') or 'production-salt-2024-very-strong'

# 根据环境变量选择配置
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
