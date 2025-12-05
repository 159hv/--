#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查数据库表结构
"""

from app import create_app, db

app = create_app()

with app.app_context():
    # 获取所有表名
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print("数据库中存在的表：")
    for table in tables:
        print(f"- {table}")
    
    # 如果存在user表，查看表结构和内容
    if 'user' in tables:
        print("\nUser表结构：")
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        columns = inspector.get_columns('user')
        for column in columns:
            print(f"- {column['name']} ({column['type']})")
        
        print("\nUser表内容：")
        from app.models.models import User
        users = User.query.all()
        if users:
            for user in users:
                print(f"- ID: {user.id}, Username: {user.username}, Email: {user.email}, Role ID: {user.role_id}")
        else:
            print("User表中没有数据！")
    else:
        print("\nUser表不存在！")