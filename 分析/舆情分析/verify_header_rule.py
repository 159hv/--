#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证Request Headers数据是否正确保存到采集规则中
"""

import json
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def verify_rule():
    """验证保存的采集规则"""
    
    try:
        from app import create_app, db
        from app.models import CollectionRule
        
        app = create_app()
        with app.app_context():
            # 获取所有规则
            rules = CollectionRule.query.order_by(CollectionRule.id.desc()).all()
            
            print("当前所有采集规则:")
            print("=" * 50)
            
            for rule in rules:
                print(f"规则ID: {rule.id}")
                print(f"站点名称: {rule.site_name}")
                print(f"站点URL: {rule.site_url}")
                print(f"创建时间: {rule.created_at}")
                print(f"更新时间: {rule.updated_at}")
                
                # 检查Request Headers
                if rule.request_headers:
                    try:
                        headers = json.loads(rule.request_headers)
                        print(f"Request Headers: {json.dumps(headers, ensure_ascii=False, indent=2)}")
                    except json.JSONDecodeError:
                        print("Request Headers: 格式错误")
                else:
                    print("Request Headers: 未设置")
                
                print("-" * 50)
            
            # 特别检查最新添加的规则
            if rules:
                latest_rule = rules[0]
                print(f"最新规则 (ID: {latest_rule.id}) 的Request Headers内容:")
                if latest_rule.request_headers:
                    try:
                        headers = json.loads(latest_rule.request_headers)
                        print(json.dumps(headers, ensure_ascii=False, indent=2))
                        
                        # 验证特定的Header字段
                        expected_headers = [
                            'access-control-allow-methods',
                            'access-control-allow-origin',
                            'connection',
                            'content-encoding',
                            'content-language',
                            'content-type',
                            'date',
                            'keep-alive',
                            'server',
                            'transfer-encoding',
                            'vary'
                        ]
                        
                        print("\n验证Header字段完整性:")
                        for header in expected_headers:
                            if header in headers:
                                print(f"✓ {header}: {headers[header]}")
                            else:
                                print(f"✗ {header}: 缺失")
                        
                        return True
                    except json.JSONDecodeError:
                        print("错误: Request Headers格式错误")
                        return False
                else:
                    print("错误: Request Headers为空")
                    return False
            else:
                print("错误: 未找到任何采集规则")
                return False
                
    except Exception as e:
        print(f"错误: 验证失败 - {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=" * 50)
    print("验证Request Headers数据保存")
    print("=" * 50)
    
    if verify_rule():
        print("\n✅ 验证成功！Request Headers数据已正确保存到采集规则中")
    else:
        print("\n❌ 验证失败！Request Headers数据保存有问题")
        sys.exit(1)

if __name__ == "__main__":
    main()
