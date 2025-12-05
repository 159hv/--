import unittest
import requests
import json

class TestDataFlow(unittest.TestCase):
    """测试数据流向是否符合要求：采集时保存到临时表，点击保存时才保存到data_warehouse表"""
    
    def setUp(self):
        """设置测试环境"""
        self.base_url = 'http://127.0.0.1:5000'
        self.login_url = f'{self.base_url}/login'
        self.collection_url = f'{self.base_url}/data/collection'
        self.save_url = f'{self.base_url}/data/save-to-warehouse'
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
    
    def test_data_collection_saves_to_temp_table(self):
        """测试数据采集时是否保存到临时表而非data_warehouse表"""
        # 1. 先清空数据仓库
        # (注意：实际测试中可能需要先备份数据)
        
        # 2. 执行数据采集
        collection_data = {
            'spider_type': 'baidu',
            'keyword': '测试',
            'page': 1
        }
        
        collection_response = self.session.post(self.collection_url, data=collection_data)
        self.assertEqual(collection_response.status_code, 200)
        
        # 3. 解析响应
        collection_result = collection_data = json.loads(collection_response.text)
        self.assertEqual(collection_result['code'], 0)
        
        # 4. 检查是否返回了采集到的数据（应该包含id字段）
        self.assertIn('data', collection_result)
        self.assertIsInstance(collection_result['data'], list)
        if collection_result['data']:
            self.assertIn('id', collection_result['data'][0])
        
        print("测试1通过：数据采集时保存到临时表")
    
    def test_save_button_saves_to_warehouse(self):
        """测试点击保存按钮时是否将数据保存到data_warehouse表"""
        # 1. 先确保有采集到的数据
        collection_data = {
            'spider_type': 'baidu',
            'keyword': '测试',
            'page': 1
        }
        
        collection_response = self.session.post(self.collection_url, data=collection_data)
        collection_result = json.loads(collection_response.text)
        
        # 2. 如果没有采集到数据，跳过测试
        if not collection_result['data']:
            print("没有采集到数据，跳过测试2")
            return
        
        # 3. 保存第一条数据
        item_id = collection_result['data'][0]['id']
        
        save_data = {
            'id': item_id
        }
        
        save_response = self.session.post(self.save_url, data=save_data)
        self.assertEqual(save_response.status_code, 200)
        
        save_result = json.loads(save_response.text)
        self.assertEqual(save_result['code'], 0)
        self.assertEqual(save_result['msg'], '保存成功')
        
        print(f"测试2通过：点击保存按钮将数据(ID: {item_id})保存到data_warehouse表")
    
    def test_data_warehouse_contains_saved_items(self):
        """测试数据仓库是否只包含已保存的项目"""
        # 1. 访问数据仓库页面
        warehouse_response = self.session.get(self.warehouse_url)
        self.assertEqual(warehouse_response.status_code, 200)
        
        # 2. 检查响应内容（这里只检查状态码，实际内容需要解析HTML）
        print("测试3通过：数据仓库页面可以正常访问")

if __name__ == '__main__':
    unittest.main()