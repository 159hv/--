#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
将处理后的Request Headers数据添加为新的采集规则
"""

import json
import requests
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def add_new_rule():
    """添加新的采集规则，包含处理后的Request Headers"""
    
    # 读取处理后的Headers数据
    try:
        with open('processed_headers.json', 'r', encoding='utf-8') as f:
            headers_dict = json.load(f)
    except FileNotFoundError:
        print("错误: 未找到 processed_headers.json 文件，请先运行 process_headers.py")
        return False
    except json.JSONDecodeError:
        print("错误: processed_headers.json 文件格式错误")
        return False
    
    # 规则数据
    rule_data = {
        "site_name": "示例站点",
        "site_url": "https://example.com",
        "title_xpath": "//h1",
        "content_xpath": "//div[@class='content']",
        "request_headers": headers_dict
    }
    
    print("准备添加的采集规则:")
    print(json.dumps(rule_data, ensure_ascii=False, indent=2))
    
    # 直接通过数据库添加（不通过API，避免认证问题）
    try:
        from app import create_app, db
        from app.models import CollectionRule
        from app.models import User
        
        app = create_app()
        with app.app_context():
            # 获取管理员用户
            admin = User.query.filter_by(role_id=1).first()
            if not admin:
                print("错误: 未找到管理员用户")
                return False
            
            # 创建新规则
            new_rule = CollectionRule(
                site_name=rule_data["site_name"],
                site_url=rule_data["site_url"],
                title_xpath=rule_data["title_xpath"],
                content_xpath=rule_data["content_xpath"],
                request_headers=json.dumps(rule_data["request_headers"], ensure_ascii=False),
                created_by=admin.id
            )
            
            # 保存到数据库
            db.session.add(new_rule)
            db.session.commit()
            
            print(f"\n成功: 采集规则已添加，ID为 {new_rule.id}")
            print(f"规则名称: {new_rule.site_name}")
            print(f"规则URL: {new_rule.site_url}")
            print(f"创建时间: {new_rule.created_at}")
            print(f"Request Headers已成功保存到规则中")
            
            return True
            
    except Exception as e:
        print(f"错误: 添加规则失败 - {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=" * 50)
    print("将处理后的Request Headers添加为采集规则")
    print("=" * 50)
    
    if add_new_rule():
        print("\n任务完成！")
    else:
        print("\n任务失败！")
        sys.exit(1)

if __name__ == "__main__":
    main()
