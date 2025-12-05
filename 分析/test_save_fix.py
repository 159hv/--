import requests
import json
import time

# 测试配置
BASE_URL = 'http://127.0.0.1:5000'
USERNAME = 'admin'
PASSWORD = 'admin123'

# 创建会话对象
session = requests.Session()

def test_login():
    """测试登录功能"""
    print("测试登录功能...")
    login_url = f'{BASE_URL}/login'
    data = {
        'username': USERNAME,
        'password': PASSWORD
    }
    response = session.post(login_url, data=data, allow_redirects=False)
    if response.status_code == 302:
        print("✓ 登录成功")
        return True
    else:
        print(f"✗ 登录失败: {response.status_code}")
        return False

def test_data_collection():
    """测试数据采集功能"""
    print("\n测试数据采集功能...")
    collection_url = f'{BASE_URL}/data/collection'
    data = {
        'spider_type': 'baidu',
        'keyword': 'test',
        'page': 1
    }
    response = session.post(collection_url, data=data)
    result = response.json()
    print(f"采集响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
    
    if result['code'] == 0:
        print(f"✓ 采集成功，新增{result['msg'].split('新增')[1].split('条')[0]}条记录")
        return result['data']
    else:
        print(f"✗ 采集失败: {result['msg']}")
        return None

def test_save_to_warehouse(collection_data):
    """测试保存到数据仓库功能"""
    if not collection_data or len(collection_data) == 0:
        print("✗ 没有数据可保存")
        return False
    
    # 检查返回的数据是否包含id字段
    first_item = collection_data[0]
    if 'id' not in first_item:
        print(f"✗ 返回的数据不包含id字段: {first_item.keys()}")
        return False
    
    item_id = first_item['id']
    print(f"\n测试保存功能，使用ID: {item_id}...")
    
    save_url = f'{BASE_URL}/data/save-to-warehouse'
    data = {
        'id': item_id
    }
    response = session.post(save_url, data=data)
    result = response.json()
    print(f"保存响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
    
    if result['code'] == 0:
        print("✓ 保存成功")
        return True
    else:
        print(f"✗ 保存失败: {result['msg']}")
        return False

def test_batch_save_to_warehouse(collection_data):
    """测试批量保存到数据仓库功能"""
    if not collection_data or len(collection_data) < 2:
        print("✗ 没有足够数据进行批量保存测试")
        return False
    
    print("\n测试批量保存功能...")
    
    # 获取前两条数据的id
    ids = [item['id'] for item in collection_data[:2]]
    print(f"批量保存ID: {ids}")
    
    save_url = f'{BASE_URL}/data/batch-save-to-warehouse'
    data = {
        'ids[]': ids
    }
    response = session.post(save_url, data=data)
    result = response.json()
    print(f"批量保存响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
    
    if result['code'] == 0:
        print("✓ 批量保存成功")
        return True
    else:
        print(f"✗ 批量保存失败: {result['msg']}")
        return False

def test_data_warehouse():
    """测试数据仓库页面"""
    print("\n测试数据仓库页面...")
    warehouse_url = f'{BASE_URL}/data/warehouse'
    response = session.get(warehouse_url)
    
    if response.status_code == 200:
        print("✓ 数据仓库页面访问成功")
        return True
    else:
        print(f"✗ 数据仓库页面访问失败: {response.status_code}")
        return False

def test_clear_collection():
    """测试清空采集结果功能"""
    print("\n测试清空采集结果功能...")
    clear_url = f'{BASE_URL}/data/clear-collection'
    response = session.post(clear_url)
    result = response.json()
    print(f"清空响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
    
    if result['code'] == 0:
        print("✓ 清空成功")
        return True
    else:
        print(f"✗ 清空失败: {result['msg']}")
        return False

if __name__ == '__main__':
    print("=== 测试数据采集保存功能修复 ===")
    
    # 执行测试
    if test_login():
        collection_data = test_data_collection()
        if collection_data:
            test_save_to_warehouse(collection_data)
            test_batch_save_to_warehouse(collection_data)
            test_data_warehouse()
        # 最后清空测试数据
        test_clear_collection()
    
    print("\n=== 测试完成 ===")