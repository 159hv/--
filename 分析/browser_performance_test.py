import time
import requests
import json
import threading
import random

# 登录系统并获取会话
def login():
    session = requests.Session()
    login_url = "http://127.0.0.1:5000/login"
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    session.post(login_url, data=login_data)
    return session

# 模拟不同网络环境的延迟
def simulate_network_delay(delay_ms):
    """模拟网络延迟"""
    time.sleep(delay_ms / 1000.0)

# 测试不同并发度下的性能
def test_concurrent_performance(session, keyword="宜宾", concurrent_levels=[1, 3, 5]):
    print("\n测试不同并发度下的性能:")
    
    for concurrency in concurrent_levels:
        print(f"\n并发度: {concurrency}")
        
        start_time = time.time()
        results = []
        
        def fetch_data():
            collection_url = "http://127.0.0.1:5000/data/collection"
            collection_data = {
                "keyword": keyword,
                "page": 1
            }
            response = session.post(collection_url, data=collection_data)
            if response.status_code == 200:
                results.append(json.loads(response.text))
            simulate_network_delay(random.randint(50, 200))  # 模拟网络延迟
        
        # 创建并发线程
        threads = []
        for i in range(concurrency):
            t = threading.Thread(target=fetch_data)
            threads.append(t)
        
        # 启动所有线程
        for t in threads:
            t.start()
        
        # 等待所有线程完成
        for t in threads:
            t.join()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        success_count = sum(1 for res in results if res.get("code") == 0)
        
        print(f"总耗时: {total_time:.2f} 秒")
        print(f"成功请求数: {success_count}/{concurrency}")
        print(f"平均响应时间: {total_time/concurrency:.2f} 秒/次")

# 测试不同网络延迟下的性能
def test_network_delay_performance(session, keyword="宜宾", delay_levels=[0, 100, 300, 500]):
    print("\n测试不同网络延迟下的性能:")
    
    for delay in delay_levels:
        print(f"\n网络延迟: {delay}ms")
        
        start_time = time.time()
        
        # 模拟网络延迟
        simulate_network_delay(delay)
        
        collection_url = "http://127.0.0.1:5000/data/collection"
        collection_data = {
            "keyword": keyword,
            "page": 1
        }
        response = session.post(collection_url, data=collection_data)
        
        # 模拟接收数据延迟
        simulate_network_delay(delay)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        if response.status_code == 200:
            data = json.loads(response.text)
            if data["code"] == 0:
                results_count = len(data["data"])
                print(f"请求成功，获取 {results_count} 条结果")
                print(f"总耗时: {total_time:.2f} 秒 (含 {delay*2}ms 模拟延迟)")
                print(f"实际处理时间: {total_time - delay*2/1000:.2f} 秒")
            else:
                print(f"请求失败: {data['msg']}")
        else:
            print(f"HTTP请求失败: 状态码 {response.status_code}")

if __name__ == "__main__":
    print("浏览器性能差异分析开始...")
    
    # 登录系统
    session = login()
    
    # 测试不同并发度
    test_concurrent_performance(session, keyword="宜宾", concurrent_levels=[1, 3, 5])
    
    # 测试不同网络延迟
    test_network_delay_performance(session, keyword="宜宾", delay_levels=[0, 100, 300, 500])
    
    print("\n性能差异分析完成！")
    print("\n可能的原因分析:")
    print("1. 网络环境差异：浏览器和Trae可能处于不同的网络环境")
    print("2. 浏览器扩展影响：某些浏览器扩展可能影响性能")
    print("3. 浏览器缓存：浏览器可能有旧的缓存数据")
    print("4. 并发处理：服务器的并发处理能力可能不足")
    print("5. 前端渲染：浏览器的DOM渲染可能比Trae慢")