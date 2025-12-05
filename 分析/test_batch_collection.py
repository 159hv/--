import requests
import json

# 登录信息
login_data = {
    'username': 'admin',
    'password': 'admin123',
    'remember': 'on'
}

# 创建会话
session = requests.Session()

# 登录
domain = 'http://127.0.0.1:5000'
login_url = f'{domain}/login'
response = session.post(login_url, data=login_data)

if response.url != login_url:
    print('✓ 登录成功')
    
    # 访问数据仓库页面获取数据列表
    warehouse_url = f'{domain}/data/warehouse'
    response = session.get(warehouse_url)
    
    if '数据仓库管理' in response.text:
        print('✓ 成功访问数据仓库页面')
        
        # 模拟批量采集，假设测试ID为1和2
        test_ids = [1, 2]  # 假设测试ID列表
        
        # 构建批量采集请求
        batch_collect_url = f'{domain}/data/warehouse/batch-detailed-collect'
        response = session.post(batch_collect_url, data={'ids[]': test_ids})
        
        try:
            result = response.json()
            print('\n批量详细采集结果:')
            print(f'状态码: {result.get("code")}')
            print(f'消息: {result.get("msg")}')
            
            if result.get('code') == 0:
                print('✓ 批量详细内容采集成功！')
                print(f'成功数量: {result.get("success_count", 0)}')
                print(f'失败数量: {result.get("failed_count", 0)}')
            else:
                print('✗ 批量详细内容采集失败')
                
        except json.JSONDecodeError:
            print('\n✗ 响应不是有效的JSON格式')
            print(f'响应内容: {response.text[:500]}...')
    
    else:
        print('✗ 无法访问数据仓库页面')
        
else:
    print('✗ 登录失败')
    print(f'响应内容: {response.text[:500]}...')
