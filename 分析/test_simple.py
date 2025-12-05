import requests

# 创建会话
session = requests.Session()

# 登录
login_url = 'http://127.0.0.1:5000/login'
login_data = {
    'username': 'admin',
    'password': 'admin123',
    'remember': 'on'
}

# 发送登录请求
response = session.post(login_url, data=login_data, allow_redirects=False)

# 检查登录是否成功
if response.status_code == 302:
    print('登录成功')
    
    # 访问数据仓库页面
    warehouse_url = 'http://127.0.0.1:5000/data/warehouse'
    response = session.get(warehouse_url)
    
    # 检查页面内容
    if '采集状态' in response.text:
        print('✓ 页面包含"采集状态"列')
    else:
        print('✗ 页面不包含"采集状态"列')
    
    if '失败原因' in response.text:
        print('✓ 页面包含"失败原因"列')
    else:
        print('✗ 页面不包含"失败原因"列')
    
    # 保存页面内容到文件以便查看
    with open('warehouse_page.html', 'w', encoding='utf-8') as f:
        f.write(response.text)
    print('页面内容已保存到warehouse_page.html文件')
else:
    print('登录失败')