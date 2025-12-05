# 测试AJAX响应

import sys
import os
import requests

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User, Role

# 创建测试应用
test_app = create_app()

def test_ajax_response():
    print("测试AJAX响应...")
    
    with test_app.test_client() as client:
        # 先登录
        print("\n1. 登录系统...")
        login_response = client.post('/login', data={
            'username': 'admin',
            'password': 'admin123',
            'remember': True
        }, follow_redirects=True)
        
        print(f"登录状态码: {login_response.status_code}")
        if login_response.status_code != 200:
            print("登录失败！")
            return
        
        # 测试数据采集API
        print("\n2. 测试数据采集API...")
        keyword = "宜宾"
        page = 1
        
        collection_response = client.post('/data/collection', data={
            'keyword': keyword,
            'page': page
        })
        
        print(f"API响应状态码: {collection_response.status_code}")
        print(f"API响应头: {collection_response.headers['Content-Type']}")
        print(f"API响应内容: {collection_response.get_data(as_text=True)}")
        
        try:
            import json
            response_data = json.loads(collection_response.get_data(as_text=True))
            print("\n3. 响应数据解析...")
            print(f"状态码: {response_data.get('code')}")
            print(f"消息: {response_data.get('msg')}")
            print(f"数据量: {len(response_data.get('data', []))}")
            
            if response_data.get('data'):
                print("\n第一条数据详情:")
                first_result = response_data['data'][0]
                for key, value in first_result.items():
                    print(f"{key}: {value}")
        except Exception as e:
            print(f"解析响应数据失败: {e}")

if __name__ == "__main__":
    # 初始化数据库
    with test_app.app_context():
        # 检查是否有管理员用户
        if not User.query.filter_by(username='admin').first():
            print("创建管理员用户...")
            admin_role = Role.query.filter_by(name='admin').first()
            if not admin_role:
                admin_role = Role(name='admin', description='管理员')
                db.session.add(admin_role)
                db.session.commit()
            
            admin_user = User(
                username='admin',
                password_hash=User.generate_password_hash('admin123'),
                role_id=admin_role.id,
                status=True
            )
            db.session.add(admin_user)
            db.session.commit()
    
    test_ajax_response()
