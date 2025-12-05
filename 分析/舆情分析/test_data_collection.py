# 测试数据采集功能

import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.spider import BaiduSpider

def test_spider():
    print("测试数据采集功能...")
    
    try:
        # 创建爬虫实例
        spider = BaiduSpider()
        
        # 测试抓取数据
        keyword = "宜宾"
        page = 1
        
        print(f"\n正在抓取关键词: {keyword}, 页码: {page}")
        results = spider.fetch_data(keyword, page)
        
        print(f"\n抓取结果: {len(results)} 条数据")
        
        if results:
            print("\n第一条结果详情:")
            first_result = results[0]
            for key, value in first_result.items():
                print(f"{key}: {value}")
        else:
            print("\n未抓取到任何结果！")
            
    except Exception as e:
        print(f"\n测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n测试完成！")

if __name__ == "__main__":
    test_spider()
