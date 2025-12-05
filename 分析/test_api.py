import requests
import json

base_url = 'http://127.0.0.1:5000'

# 创建会话
session = requests.Session()

# 1. 登录系统
print("登录系统...")
login_data = {
    'username': 'admin',
    'password': 'admin123'
}
response = session.post(f'{base_url}/login', data=login_data)
print(f"登录响应状态: {response.status_code}")

# 2. 测试数据采集接口
print("\n测试数据采集接口...")
collection_data = {
    'spider_type': 'baidu',
    'keyword': 'test',
    'page': 1
}
response = session.post(f'{base_url}/data/collection', data=collection_data)
print(f"数据采集响应状态: {response.status_code}")
try:
    print(f"数据采集响应: {response.json()}")
except requests.exceptions.JSONDecodeError:
    print(f"数据采集响应内容: {response.text[:200]}...")

# 3. 测试获取采集结果
print("\n测试获取采集结果...")
response = session.get(f'{base_url}/data/collection')
print(f"获取采集结果响应状态: {response.status_code}")

# 4. 测试数据仓库页面
print("\n测试数据仓库页面...")
response = session.get(f'{base_url}/data/warehouse')
print(f"数据仓库页面响应状态: {response.status_code}")

# 5. 测试清空采集结果
print("\n测试清空采集结果...")
response = session.post(f'{base_url}/data/clear-collection')
print(f"清空采集结果响应状态: {response.status_code}")
try:
    print(f"清空采集结果响应: {response.json()}")
except requests.exceptions.JSONDecodeError:
    print(f"清空采集结果响应内容: {response.text[:200]}...")
