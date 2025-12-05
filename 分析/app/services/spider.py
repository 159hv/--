import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import quote_plus, urljoin
import json
import threading
from concurrent.futures import ThreadPoolExecutor

class BaiduSpider:
    """百度搜索数据抓取模块"""
    
    # 类级别的线程池，用于异步执行采集任务
    _executor = ThreadPoolExecutor(max_workers=4)
    
    def __init__(self):
        """初始化抓取模块"""
        self.base_url = "https://www.baidu.com/s?wd={}"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Referer": "https://www.baidu.com/",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache"
        }
        self.cookies = {
            "BAIDUID": "156B6802D08C1905F9754D9B2F15C8A8:FG=1",
            "BDUSS": "FMzY1p5dk9tT3hGcTlCbEpKT3prOTZWRURDNVVKVlpKNmFqeURUb2xoVzlrVlJwSVFBQUFBJCQAAAAAAQAAAAEAAAAkrMCbZXV1ZWQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAL0ELWm9BC1pN",
            "BDORZ": "B490B5EBF6F3CD402E515D22BCDA1598",
            "H_PS_PSSID": "63146_66126_66211_66226_66245_66288_66261_66393_66516_66529_66545_66579_66586_66593_66603_66605_66639_66648_66663_66694_66716_66744_66616_66777_66787_66793_66801_66805_66599"
        }
    
    def fetch_data(self, keyword, page=1):
        """
        抓取百度搜索结果数据（同步版本）
        
        Args:
            keyword (str): 搜索关键词
            page (int): 页码
            
        Returns:
            list: 搜索结果列表，每个元素包含标题、概要、封面、原始URL和来源
        """
        try:
            # 构建搜索URL
            encoded_keyword = quote_plus(keyword)
            url = self.base_url.format(encoded_keyword)
            if page > 1:
                url += f"&pn={((page-1)*10)}"
            
            # 发送请求
            response = requests.get(
                url,
                headers=self.headers,
                cookies=self.cookies,
                timeout=10
            )
            response.encoding = 'utf-8'
            
            if response.status_code != 200:
                print(f"请求失败，状态码：{response.status_code}")
                return []
            
            # 解析HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            
            # 查找搜索结果列表
            search_results = soup.find_all('div', class_='result')
            
            for item in search_results:
                try:
                    # 提取标题
                    title_tag = item.find('h3', class_='t')
                    if not title_tag:
                        continue
                    
                    title = title_tag.text.strip()
                    
                    # 提取原始URL
                    link_tag = title_tag.find('a')
                    if not link_tag or not link_tag.get('href'):
                        continue
                    
                    original_url = link_tag.get('href')
                    
                    # 提取摘要（尝试多种可能的CSS类）
                    abstract = ""
                    abstract_tags = [
                        item.find('span', class_='summary-text_560AW'),  # 新的摘要class
                        item.find('div', class_='c-abstract'),
                        item.find('div', class_='content-right_8Zs40'),
                        item.find('div', class_='c-summary-160s'),
                        item.find('div', class_='c-summary')
                    ]
                    for tag in abstract_tags:
                        if tag:
                            abstract = tag.text.strip()
                            break
                    
                    # 提取来源（尝试多种可能的CSS类）
                    source = ""
                    source_tags = [
                        item.find('span', class_='cosc-source-text'),  # 新的来源class
                        item.find('span', class_='cosc-source'),  # 新的来源class
                        item.find('div', class_='cosc-source'),  # 新的来源class
                        item.find('a', class_='c-showurl'),
                        item.find('span', class_='c-showurl'),
                        item.find('div', class_='c-showurl'),
                        item.find('span', class_='site-host')
                    ]
                    for tag in source_tags:
                        if tag:
                            source = tag.text.strip()
                            break
                    
                    # 如果没有找到来源，尝试从URL中提取
                    if not source and original_url:
                        from urllib.parse import urlparse
                        parsed_url = urlparse(original_url)
                        source = parsed_url.netloc
                    
                    # 提取封面图片
                    img_tag = item.find('img', class_='general_image_pic')
                    cover = img_tag.get('src') if img_tag else ""
                    
                    # 如果没有找到图片，尝试从其他地方提取
                    if not cover:
                        img_match = re.search(r'<img[^>]+src="([^"]+)"[^>]*>', str(item))
                        if img_match:
                            cover = img_match.group(1)
                    
                    # 添加到结果列表
                    results.append({
                        "title": title,
                        "summary": abstract,  # 将abstract改为summary
                        "cover": cover,
                        "url": original_url,  # 将original_url改为url
                        "source": source
                    })
                    
                except Exception as e:
                    print(f"解析单个结果失败：{e}")
                    continue
            
            return results
            
        except Exception as e:
            print(f"抓取数据失败：{e}")
            return []
    
    def fetch_data_async(self, keyword, page=1):
        """
        抓取百度搜索结果数据（异步版本）
        
        Args:
            keyword (str): 搜索关键词
            page (int): 页码
            
        Returns:
            Future: 异步执行的Future对象，结果为搜索结果列表
        """
        return self._executor.submit(self.fetch_data, keyword, page)
    
    def fetch_images(self, keyword, page=1):
        """
        抓取百度图片搜索结果
        
        Args:
            keyword (str): 搜索关键词
            page (int): 页码
            
        Returns:
            list: 图片结果列表
        """
        try:
            url = f"https://image.baidu.com/search/index?tn=baiduimage&word={quote_plus(keyword)}"
            if page > 1:
                url += f"&pn={((page-1)*30)}"
            
            response = requests.get(
                url,
                headers=self.headers,
                cookies=self.cookies,
                timeout=10
            )
            response.encoding = 'utf-8'
            
            if response.status_code != 200:
                print(f"图片请求失败，状态码：{response.status_code}")
                return []
            
            # 提取图片数据
            img_results = []
            # 使用正则表达式提取图片信息
            img_pattern = re.compile(r'"objURL":"([^"]+)"')
            img_urls = img_pattern.findall(response.text)
            
            for img_url in img_urls[:10]:  # 只取前10张图片
                img_results.append({
                    "url": img_url,
                    "keyword": keyword
                })
            
            return img_results
            
        except Exception as e:
            print(f"抓取图片失败：{e}")
            return []

class XinhuaSpider:
    """新华网数据抓取模块"""
    
    # 类级别的线程池，用于异步执行采集任务
    _executor = ThreadPoolExecutor(max_workers=4)
    
    def __init__(self):
        """初始化抓取模块"""
        self.base_url = "http://sc.news.cn/scyw.htm"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Referer": "http://sc.news.cn/",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache"
        }
    
    def fetch_data(self, keyword=None, page=1):
        """
        抓取新华网四川要闻数据
        
        Args:
            keyword (str): 搜索关键词（暂不支持搜索，仅抓取四川要闻）
            page (int): 页码
            
        Returns:
            list: 搜索结果列表，每个元素包含标题、概要、封面、原始URL和来源
        """
        try:
            # 构建URL（目前仅支持四川要闻首页，页码暂不支持）
            url = self.base_url
            
            # 发送请求
            response = requests.get(
                url,
                headers=self.headers,
                timeout=10
            )
            response.encoding = 'utf-8'
            
            if response.status_code != 200:
                print(f"请求失败，状态码：{response.status_code}")
                return []
            
            # 解析HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            
            # 查找新闻列表
            news_list = soup.find('div', class_='scpd_page_box')
            if not news_list:
                print("未找到新闻列表")
                return []
            
            # 查找所有新闻条目
            news_items = news_list.find_all('a', href=True)
            
            for item in news_items:
                try:
                    # 提取标题
                    title_tag = item.find('dt')
                    if not title_tag:
                        continue
                    
                    title = title_tag.text.strip()
                    
                    # 提取原文URL
                    original_url = item.get('href')
                    # 处理相对URL
                    if original_url and not original_url.startswith(('http://', 'https://')):
                        original_url = urljoin(self.base_url, original_url)
                    
                    # 提取摘要
                    abstract_tag = item.find('dd')
                    abstract = abstract_tag.text.strip() if abstract_tag else ""
                    
                    # 提取来源（新华网四川频道）
                    source = "新华网"
                    
                    # 提取封面图片
                    img_tag = item.find('img', class_='scpd_auto_pic')
                    cover = ""
                    if img_tag:
                        img_src = img_tag.get('src')
                        if img_src:
                            # 处理相对图片URL
                            if img_src.startswith('http://') or img_src.startswith('https://'):
                                cover = img_src
                            else:
                                cover = urljoin(self.base_url, img_src)
                    
                    # 添加到结果列表
                    results.append({
                        "title": title,
                        "summary": abstract,  # 保持与百度新闻一致的字段名
                        "cover": cover,
                        "url": original_url,  # 保持与百度新闻一致的字段名
                        "source": source
                    })
                    
                except Exception as e:
                    print(f"解析单个新闻失败：{e}")
                    continue
            
            # 如果需要支持分页，可以在这里根据page参数截取结果
            # 由于当前页面结构不支持页码，暂时返回全部结果
            if page > 1:
                start = (page - 1) * 10
                end = start + 10
                results = results[start:end]
            else:
                results = results[:10]  # 每页返回10条数据
            
            return results
            
        except Exception as e:
            print(f"抓取新华网数据失败：{e}")
            return []
    
    def fetch_data_async(self, keyword=None, page=1):
        """
        异步抓取新华网数据
        
        Args:
            keyword (str): 搜索关键词
            page (int): 页码
            
        Returns:
            Future: 异步执行的Future对象
        """
        return self._executor.submit(self.fetch_data, keyword, page)

# 测试代码
if __name__ == "__main__":
    print("=== 测试百度爬虫 ===")
    baidu_spider = BaiduSpider()
    
    # 测试搜索功能
    keyword = "人工智能"
    print(f"正在搜索：{keyword}")
    
    results = baidu_spider.fetch_data(keyword, page=1)
    print(f"找到 {len(results)} 条结果")
    
    for i, result in enumerate(results[:3]):  # 只显示前3条结果
        print(f"\n结果 {i+1}:")
        print(f"标题：{result['title']}")
        print(f"摘要：{result['summary']}")
        print(f"封面：{result['cover']}")
        print(f"URL：{result['url']}")
        print(f"来源：{result['source']}")
    
    print("\n=== 测试新华爬虫 ===")
    xinhua_spider = XinhuaSpider()
    
    # 测试抓取四川要闻
    print("正在抓取新华网四川要闻...")
    
    xinhua_results = xinhua_spider.fetch_data(page=1)
    print(f"找到 {len(xinhua_results)} 条结果")
    
    for i, result in enumerate(xinhua_results[:3]):  # 只显示前3条结果
        print(f"\n结果 {i+1}:")
        print(f"标题：{result['title']}")
        print(f"摘要：{result['summary']}")
        print(f"封面：{result['cover']}")
        print(f"URL：{result['url']}")
        print(f"来源：{result['source']}")
