#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
处理用户提供的Request Headers数据
"""

import json

# 用户提供的Request Headers字符串
headers_str = '''
access-control-allow-methods
GET, POST, OPTIONS
access-control-allow-origin
*
connection
keep-alive
content-encoding
gzip
content-language
zh-CN
content-type
text/html;charset=utf-8
date
Fri, 05 Dec 2025 02:08:16 GMT
keep-alive
timeout=5
server
nginx
transfer-encoding
chunked
vary
Accept-Encoding
'''

def process_headers(headers_str):
    """将原始Headers字符串转换为JSON格式"""
    # 移除首尾空白行
    headers_str = headers_str.strip()
    
    # 按行分割
    lines = headers_str.split('\n')
    
    # 确保行数为偶数（键值对）
    if len(lines) % 2 != 0:
        raise ValueError("Headers格式错误：键值对数量不匹配")
    
    headers_dict = {}
    
    # 按顺序处理键值对
    for i in range(0, len(lines), 2):
        key = lines[i].strip()
        value = lines[i+1].strip()
        headers_dict[key] = value
    
    return headers_dict

def main():
    try:
        # 处理Headers数据
        headers_dict = process_headers(headers_str)
        
        # 转换为JSON格式
        headers_json = json.dumps(headers_dict, ensure_ascii=False, indent=2)
        
        print("处理后的Request Headers (JSON格式):")
        print(headers_json)
        
        # 保存到文件
        with open('processed_headers.json', 'w', encoding='utf-8') as f:
            f.write(headers_json)
        
        print("\nHeaders数据已保存到 processed_headers.json 文件")
        
        return headers_dict
    except Exception as e:
        print(f"处理失败: {str(e)}")
        return None

if __name__ == "__main__":
    main()
