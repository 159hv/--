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
        
        # 获取数据仓库中的第一条记录ID（这里简化处理，实际可能需要解析HTML）
        # 我们可以通过API获取数据，假设API存在
        print('尝试获取数据仓库中的记录...')
        
        # 模拟获取第一条记录的ID
        # 实际项目中可能需要使用API或解析HTML获取ID
        test_record_id = 1  # 假设测试ID为1
        
        # 尝试详细采集
        collect_url = f'{domain}/data/warehouse/detailed-collect/{test_record_id}'
        response = session.post(collect_url)
        
        try:
            result = response.json()
            print('\n详细采集结果:')
            print(f'状态码: {result.get("code")}')
            print(f'消息: {result.get("msg")}')
            
            if result.get('code') == 0:
                print('✓ 详细内容采集成功！')
                
                # 查看详细采集结果
                print('\n正在获取详细采集内容...')
                
                # 假设存在API可以获取详细内容
                # 这里只是示例，实际项目中可能需要调整
                detail_url = f'{domain}/data/warehouse/detail/{test_record_id}'
                response = session.get(detail_url)
                
                if response.status_code == 200:
                    print('✓ 成功获取详细内容')
                    # 可以进一步解析详细内容
                
            else:
                print('✗ 详细内容采集失败')
                
        except json.JSONDecodeError:
            print('\n✗ 响应不是有效的JSON格式')
            print(f'响应内容: {response.text[:500]}...')
    
    else:
        print('✗ 无法访问数据仓库页面')
        
else:
    print('✗ 登录失败')
    print(f'响应内容: {response.text[:500]}...')
