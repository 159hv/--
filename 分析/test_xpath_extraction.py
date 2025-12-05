import requests
from lxml import etree

# 测试URL和XPath
# 使用我们测试过的URL
url = 'http://example.com/article.html'  # 这里需要替换为真实的测试URL

# 使用测试记录的来源
from app.models import CollectionRule, DataWarehouse
from app import create_app, db

app = create_app()
with app.app_context():
    # 获取测试记录
    test_record_id = 1
    topic = DataWarehouse.query.get(test_record_id)
    
    if topic:
        print(f'测试记录ID: {topic.id}')
        print(f'标题: {topic.title}')
        print(f'URL: {topic.url}')
        print(f'来源: {topic.source}')
        
        # 获取对应的采集规则
        rule = CollectionRule.query.filter_by(site_name=topic.source).first()
        
        if rule:
            print(f'\n采集规则:')
            print(f'标题XPath: {rule.title_xpath}')
            print(f'内容XPath: {rule.content_xpath}')
            
            # 发送请求获取页面内容
            response = requests.get(topic.url, timeout=10)
            response.encoding = response.apparent_encoding
            html = response.text
            
            # 保存HTML到文件以便分析
            with open('test_xpath_page.html', 'w', encoding='utf-8') as f:
                f.write(html)
            print('\n页面内容已保存到 test_xpath_page.html')
            
            # 使用lxml解析HTML
            tree = etree.HTML(html)
            
            # 测试标题XPath
            print('\n测试标题XPath:')
            title_elements = tree.xpath(rule.title_xpath)
            print(f'匹配到 {len(title_elements)} 个标题元素')
            if title_elements:
                for i, elem in enumerate(title_elements[:3]):  # 只显示前3个
                    text = elem.xpath("string()").strip()
                    print(f'标题元素 {i+1}: "{text}"')
            
            # 测试内容XPath
            print('\n测试内容XPath:')
            content_elements = tree.xpath(rule.content_xpath)
            print(f'匹配到 {len(content_elements)} 个内容元素')
            if content_elements:
                for i, elem in enumerate(content_elements[:3]):  # 只显示前3个
                    text = elem.xpath("string()").strip()
                    print(f'内容元素 {i+1} 长度: {len(text)}')
                    print(f'内容元素 {i+1} 开头: "{text[:50]}..."')
            
            # 尝试使用一些常见的内容XPath
            print('\n尝试使用常见内容XPath:')
            common_content_xpaths = [
                '//article',
                '//div[contains(@class, "content")]',
                '//div[contains(@class, "article")]',
                '//div[contains(@id, "content")]',
                '//section[contains(@class, "main")]',
                '//div[contains(@class, "post")]'
            ]
            
            for xpath in common_content_xpaths:
                elements = tree.xpath(xpath)
                if elements:
                    text = elements[0].xpath("string()").strip()
                    print(f'XPath {xpath}: 匹配到 {len(elements)} 个元素, 内容长度 {len(text)}')
        else:
            print(f'未找到来源为 {topic.source} 的采集规则')
    else:
        print(f'未找到ID为 {test_record_id} 的测试记录')
