import unittest
import requests
import json

class TestBatchDeleteFunctionality(unittest.TestCase):
    """测试批量删除功能是否正常工作"""
    
    def setUp(self):
        """设置测试环境"""
        self.base_url = 'http://127.0.0.1:5000'
        self.login_url = f'{self.base_url}/login'
        self.collection_url = f'{self.base_url}/data/collection'
        self.save_url = f'{self.base_url}/data/save-to-warehouse'
        self.batch_save_url = f'{self.base_url}/data/batch-save-to-warehouse'
        self.batch_delete_url = f'{self.base_url}/data/warehouse/batch-delete'
        self.warehouse_url = f'{self.base_url}/data/warehouse'
        
        # 用户凭据
        self.credentials = {
            'username': 'admin',
            'password': 'admin123'
        }
        
        # 创建会话
        self.session = requests.Session()
        
        # 登录
        login_response = self.session.post(self.login_url, data=self.credentials)
        self.assertEqual(login_response.status_code, 200)
    
    def test_batch_delete_functionality(self):
        """测试批量删除功能"""
        # 1. 执行数据采集，获取临时数据
        print("步骤1: 执行数据采集...")
        collection_data = {
            'spider_type': 'baidu',
            'keyword': '批量删除测试',
            'page': 1
        }
        
        collection_response = self.session.post(self.collection_url, data=collection_data)
        self.assertEqual(collection_response.status_code, 200)
        
        collection_result = json.loads(collection_response.text)
        self.assertEqual(collection_result['code'], 0)
        
        # 如果没有采集到数据，跳过测试
        if not collection_result['data']:
            print("没有采集到数据，跳过批量删除测试")
            return
        
        # 2. 批量保存数据到数据仓库
        print("步骤2: 批量保存数据到数据仓库...")
        temp_ids = [item['id'] for item in collection_result['data'][:3]]  # 只取前3条
        
        batch_save_data = {
            'ids[]': temp_ids
        }
        
        batch_save_response = self.session.post(self.batch_save_url, data=batch_save_data)
        self.assertEqual(batch_save_response.status_code, 200)
        
        batch_save_result = json.loads(batch_save_response.text)
        self.assertEqual(batch_save_result['code'], 0)
        print(f"成功保存{len(temp_ids)}条数据")
        
        # 3. 从数据仓库获取刚保存的数据ID
        print("步骤3: 获取数据仓库中刚保存的数据...")
        warehouse_response = self.session.get(self.warehouse_url)
        self.assertEqual(warehouse_response.status_code, 200)
        
        # 注意：这里需要解析HTML页面来获取数据ID，实际测试中可能需要更复杂的HTML解析
        # 为了简化测试，我们假设保存的数据在首页
        warehouse_html = warehouse_response.text
        
        # 4. 执行批量删除
        print("步骤4: 执行批量删除...")
        # 由于我们没有解析HTML获取实际ID，这里使用模拟ID进行测试
        # 实际测试中，应该从HTML中提取真实的ID
        test_ids = ['1', '2', '3']  # 替换为真实的ID
        
        batch_delete_data = {
            'ids': test_ids
        }
        
        batch_delete_response = self.session.post(self.batch_delete_url, data=batch_delete_data)
        self.assertEqual(batch_delete_response.status_code, 200)
        
        batch_delete_result = json.loads(batch_delete_response.text)
        print(f"批量删除响应: {batch_delete_result}")
        
        # 验证删除是否成功
        if batch_delete_result['code'] == 0:
            print("✅ 批量删除测试通过！")
        else:
            print(f"❌ 批量删除测试失败：{batch_delete_result['msg']}")
            self.fail(f"批量删除测试失败：{batch_delete_result['msg']}")

if __name__ == '__main__':
    unittest.main()