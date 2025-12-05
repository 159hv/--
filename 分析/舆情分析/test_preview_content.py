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
    
    # 测试ID
    test_record_id = 1
    
    # 先执行详细采集
    collect_url = f'{domain}/data/warehouse/detailed-collect/{test_record_id}'
    response = session.post(collect_url)
    
    print('\n详细采集结果:')
    try:
        result = response.json()
        print(f'状态码: {result.get("code")}')
        print(f'消息: {result.get("msg")}')
    except json.JSONDecodeError:
        print('响应不是有效的JSON')
        print(response.text)
    
    # 然后获取详细内容，模拟预览功能
    print('\n获取详细内容(模拟预览):')
    detail_url = f'{domain}/data/warehouse/detailed-content/{test_record_id}'
    response = session.get(detail_url)
    
    try:
        result = response.json()
        print(f'状态码: {result.get("code")}')
        print(f'消息: {result.get("msg")}')
        
        if result.get("code") == 0:
            data = result.get("data", {})
            print(f'\n详细内容数据:')
            print(f'标题: "{data.get("detailed_title", "")}"')
            content = data.get("detailed_content", "")
            print(f'内容长度: {len(content)} 字符')
            print(f'内容开头: "{content[:100]}..."' if content else '内容为空')
            print(f'是否采集: {data.get("is_collected")}')
            print(f'采集时间: {data.get("collected_at")}')
            print(f'错误信息: "{data.get("collection_error", "")}"')
            
            if not data.get("detailed_title") and not data.get("detailed_content"):
                print('\n⚠️  警告: 详细内容为空')
    except json.JSONDecodeError:
        print('响应不是有效的JSON')
        print(response.text)
else:
    print('✗ 登录失败')
    print(response.text)
