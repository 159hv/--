import os
import sys
from flask import Flask
from app import create_app, db
from app.models import User, Role, Setting, Topic, Keyword, TopicKeyword
from werkzeug.security import generate_password_hash

# 创建Flask应用实例
app = create_app()

with app.app_context():
    # 删除所有表
    db.drop_all()
    
    # 创建所有表
    db.create_all()
    
    # 创建默认角色
    admin_role = Role(name='admin', description='管理员角色，拥有所有权限')
    user_role = Role(name='user', description='普通用户角色，可以查看数据和报告')
    
    db.session.add(admin_role)
    db.session.add(user_role)
    db.session.commit()
    
    # 创建默认管理员用户
    admin_user = User(
        username='admin',
        password='admin123',  # 使用password属性自动生成哈希
        email='admin@example.com',
        role_id=admin_role.id,
        status=True  # 使用布尔值
    )
    
    # 创建默认普通用户
    normal_user = User(
        username='user',
        password='user123',  # 使用password属性自动生成哈希
        email='user@example.com',
        role_id=user_role.id,
        status=True  # 使用布尔值
    )
    
    db.session.add(admin_user)
    db.session.add(normal_user)
    db.session.commit()
    
    # 创建系统设置
    app_settings = [
        Setting(key='app_name', value='政企智能舆情分析系统', description='应用名称'),
        Setting(key='app_logo', value='', description='应用LOGO路径'),
        Setting(key='default_topic', value='舆情分析', description='默认话题'),
    ]
    
    for setting in app_settings:
        db.session.add(setting)
    
    db.session.commit()
    
    print('数据库初始化完成！')
    print('默认管理员账号：admin / admin123')
    print('默认普通用户账号：user / user123')
