import requests
import re

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

if '登录成功' in response.text or response.url != login_url:
    print('登录成功')
    
    # 访问数据仓库页面
    warehouse_url = f'{domain}/data/warehouse'
    response = session.get(warehouse_url)
    
    if '数据仓库管理' in response.text:
        print('成功访问数据仓库页面')
        
        # 检查是否包含采集状态和失败原因列
        if '采集状态' in response.text and '失败原因' in response.text:
            print('✓ 已成功添加采集状态和失败原因列')
            
            # 检查表格中是否有采集状态显示
            if 'class="layui-table"' in response.text:
                print('✓ 表格渲染正常')
                
                # 提取所有采集状态
                status_pattern = re.compile(r'<span style="color:(green|red|gray)">(成功|失败|未采集)</span>')
                status_matches = status_pattern.findall(response.text)
                
                if status_matches:
                    print('✓ 成功显示采集状态')
                    print('  状态统计:')
                    print(f'    成功: {status_matches.count("成功")}')
                    print(f'    失败: {status_matches.count("失败")}')
                    print(f'    未采集: {status_matches.count("未采集")}')
                else:
                    print('✓ 表格已添加状态列，但目前没有采集记录')
        else:
            print('✗ 未找到采集状态和失败原因列')
    else:
        print('✗ 无法访问数据仓库页面')
else:
    print('✗ 登录失败')