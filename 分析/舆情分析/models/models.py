
from app import db
from flask_login import UserMixin
from datetime import datetime

class Role(db.Model):
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    users = db.relationship('User', backref='role', lazy='dynamic')
    
    def __repr__(self):
        return '<Role {}>'.format(self.name)

class User(UserMixin, db.Model):
    """用户模型"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    email = db.Column(db.String(120), index=True, unique=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), default=2)  # 默认普通用户角色
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    status = db.Column(db.Boolean, default=True)  # 用户状态：启用/禁用
    
    def __repr__(self):
        return '<User {}>'.format(self.username)
    
    @property
    def is_admin(self):
        """检查用户是否为管理员"""
        return self.role_id == 1  # 假设角色ID为1是管理员
    
    @property
    def password(self):
        """获取密码（实际上返回None，因为不存储明文密码）"""
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        """设置密码，生成密码哈希值"""
        from werkzeug.security import generate_password_hash
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """验证密码"""
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, password)

class Topic(db.Model):
    """舆情话题模型"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), nullable=False)
    content = db.Column(db.Text, nullable=False)
    source = db.Column(db.String(128))  # 信息来源
    url = db.Column(db.String(512))
    published_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    sentiment = db.Column(db.Float)  # 情感得分
    
    def __repr__(self):
        return '<Topic {}>'.format(self.title)

class DataWarehouse(db.Model):
    """数据仓库模型"""
    __tablename__ = 'data_warehouse'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), nullable=False)
    content = db.Column(db.Text, nullable=False)
    source = db.Column(db.String(128))  # 信息来源
    url = db.Column(db.String(512))
    published_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    collected_by = db.Column(db.Integer, db.ForeignKey('user.id'))  # 采集者
    
    user = db.relationship('User', backref=db.backref('warehouse_data', lazy='dynamic'))
    
    def __repr__(self):
        return '<DataWarehouse {}>'.format(self.title)

class Keyword(db.Model):
    """关键词模型"""
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(64), index=True, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return '<Keyword {}>'.format(self.word)

class TopicKeyword(db.Model):
    """话题关键词关联模型"""
    id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'))
    keyword_id = db.Column(db.Integer, db.ForeignKey('keyword.id'))
    weight = db.Column(db.Float)  # 关键词权重
    
    topic = db.relationship('Topic', backref=db.backref('topic_keywords', lazy='dynamic'))
    keyword = db.relationship('Keyword', backref=db.backref('keyword_topics', lazy='dynamic'))
    
    def __repr__(self):
        return '<TopicKeyword topic_id={}, keyword_id={}>'.format(self.topic_id, self.keyword_id)

class CollectionTemp(db.Model):
    """采集临时存储模型"""
    __tablename__ = 'collection_temp'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), nullable=False)
    content = db.Column(db.Text, nullable=False)
    summary = db.Column(db.Text)  # 摘要
    source = db.Column(db.String(128))  # 信息来源
    url = db.Column(db.String(512))
    cover = db.Column(db.String(512))  # 封面图片
    published_at = db.Column(db.DateTime, index=True)
    collected_at = db.Column(db.DateTime, default=datetime.utcnow)  # 采集时间
    is_deep_collected = db.Column(db.Boolean, default=False)  # 是否深度采集
    collected_by = db.Column(db.Integer, db.ForeignKey('user.id'))  # 采集者
    
    user = db.relationship('User', backref=db.backref('collections', lazy='dynamic'))
    
    def __repr__(self):
        return '<CollectionTemp {}>'.format(self.title)

class Setting(db.Model):
    __tablename__ = 'settings'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return '<Setting {}: {}>'.format(self.key, self.value)

class CollectionRule(db.Model):
    """采集规则模型"""
    __tablename__ = 'collection_rules'
    
    id = db.Column(db.Integer, primary_key=True)
    site_name = db.Column(db.String(100), nullable=False)
    site_url = db.Column(db.String(500), nullable=False)
    title_xpath = db.Column(db.String(255), nullable=False)
    content_xpath = db.Column(db.String(255), nullable=False)
    request_headers = db.Column(db.Text)  # 存储为JSON字符串
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))  # 关联用户
    
    user = db.relationship('User', backref=db.backref('collection_rules', lazy='dynamic'))
    
    def __repr__(self):
        return '<CollectionRule {}>'.format(self.site_name)

class DetailedContent(db.Model):
    """详细采集内容模型"""
    __tablename__ = 'detailed_content'
    
    id = db.Column(db.Integer, primary_key=True)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('data_warehouse.id'), nullable=False, unique=True)
    detailed_title = db.Column(db.String(512))  # 详细标题
    detailed_content = db.Column(db.Text)  # 详细内容
    raw_html = db.Column(db.Text)  # 原始HTML
    collected_at = db.Column(db.DateTime, default=datetime.utcnow)  # 采集时间
    is_collected = db.Column(db.Boolean, default=True)  # 是否成功采集
    collection_error = db.Column(db.Text)  # 采集错误信息
    
    # 关联到数据仓库
    warehouse = db.relationship('DataWarehouse', backref=db.backref('detailed_content', uselist=False))
    
    def __repr__(self):
        return '<DetailedContent warehouse_id={}>'.format(self.warehouse_id)


class AiEngine(db.Model):
    """AI引擎模型"""
    __tablename__ = 'ai_engines'
    
    id = db.Column(db.Integer, primary_key=True)
    provider_name = db.Column(db.String(100), nullable=False)  # 服务商名称
    api_url = db.Column(db.String(500), nullable=False)  # API URL
    api_key = db.Column(db.String(255), nullable=False)  # API Key
    model_name = db.Column(db.String(100), nullable=False)  # 模型名称
    description = db.Column(db.Text)  # 引擎描述
    status = db.Column(db.Boolean, default=True)  # 引擎状态：启用/禁用
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 创建时间
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))  # 创建者
    
    # 关联到用户
    user = db.relationship('User', backref=db.backref('ai_engines', lazy='dynamic'))
    
    def __repr__(self):
        return '<AiEngine {}>'.format(self.provider_name)