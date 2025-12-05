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
    collection_result = response.json()
    print(f"数据采集响应: {collection_result}")
    
    # 3. 测试保存到数据仓库
    print("\n测试保存到数据仓库...")
    # 从采集结果中获取第一条数据的ID
    if collection_result['code'] == 0 and collection_result['data']:
        # 注意：这里的data字段是采集的内容，而不是数据库中的ID
        # 我们需要先获取数据库中的ID
        response = session.get(f'{base_url}/data/collection')
        if response.status_code == 200:
            # 由于返回的是HTML页面，我们需要解析页面来获取ID
            print("成功获取采集结果页面")
            print("由于返回的是HTML页面，无法自动解析ID进行测试")
            print("请通过浏览器手动测试保存功能")
except requests.exceptions.JSONDecodeError:
    print(f"数据采集响应内容: {response.text[:200]}...")

# 4. 测试批量保存到数据仓库
print("\n测试批量保存到数据仓库...")
# 这里需要知道采集结果的ID，实际测试时需要先进行数据采集并获取ID
# response = session.post(f'{base_url}/data/batch-save-to-warehouse', data={'ids[]': [1, 2]})
# print(f"批量保存到数据仓库响应: {response.json()}")

# 5. 测试数据仓库页面
print("\n测试数据仓库页面...")
response = session.get(f'{base_url}/data/warehouse')
print(f"数据仓库页面响应状态: {response.status_code}")

# 6. 测试清空采集结果
print("\n测试清空采集结果...")
response = session.post(f'{base_url}/data/clear-collection')
print(f"清空采集结果响应状态: {response.status_code}")
try:
    print(f"清空采集结果响应: {response.json()}")
except requests.exceptions.JSONDecodeError:
    print(f"清空采集结果响应内容: {response.text[:200]}...")
