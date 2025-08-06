#!/usr/bin/env python3
"""
测试已放弃功能的示例脚本
注意：这个脚本需要在Flask应用运行时执行
"""

import requests
import json
from datetime import datetime

# 服务器地址
BASE_URL = "http://localhost:5000"

def test_abandon_feature():
    """测试已放弃功能"""
    
    print("=== Todo List 已放弃功能测试 ===\n")
    
    # 1. 创建一个测试待办事项
    print("1. 创建测试待办事项...")
    create_data = {
        "todo": "测试待办事项 - 将被放弃",
        "status": "未完成",
        "todo_time": "2024-12-20 15:00:00",
        "created_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    try:
        response = requests.post(f"{BASE_URL}/todolist", json=create_data)
        print(f"创建结果: {response.text}")
    except requests.exceptions.ConnectionError:
        print("错误: 无法连接到服务器，请确保Flask应用正在运行")
        return
    
    # 2. 查询所有待办事项（应该包含刚创建的）
    print("\n2. 查询所有待办事项...")
    try:
        response = requests.get(f"{BASE_URL}/todolist")
        todos = json.loads(response.text)
        print(f"当前待办事项数量: {len(todos)}")
        
        if todos:
            test_id = todos[-1]['id']  # 获取最后一个（刚创建的）待办事项ID
            print(f"测试用待办事项ID: {test_id}")
            
            # 3. 放弃这个待办事项
            print(f"\n3. 放弃待办事项 ID: {test_id}...")
            abandon_data = {"todolist_id": test_id}
            response = requests.put(f"{BASE_URL}/todolist/abandon", json=abandon_data)
            print(f"放弃结果: {response.text}")
            
            # 4. 再次查询所有待办事项（应该不包含已放弃的）
            print("\n4. 查询所有活跃待办事项（应该排除已放弃的）...")
            response = requests.get(f"{BASE_URL}/todolist")
            active_todos = json.loads(response.text)
            print(f"活跃待办事项数量: {len(active_todos)}")
            
            # 检查是否还包含被放弃的项目
            abandoned_found = any(todo['id'] == test_id for todo in active_todos)
            print(f"已放弃的项目是否还在活跃列表中: {'是' if abandoned_found else '否'}")
            
            # 5. 查询已放弃的待办事项
            print("\n5. 查询已放弃的待办事项...")
            response = requests.get(f"{BASE_URL}/todolist?status=已放弃")
            abandoned_todos = json.loads(response.text)
            print(f"已放弃待办事项数量: {len(abandoned_todos)}")
            
            if abandoned_todos:
                print("已放弃的待办事项:")
                for todo in abandoned_todos:
                    print(f"  - ID: {todo['id']}, 内容: {todo['todo']}, 状态: {todo['status']}, 放弃时间: {todo['do_time']}")
            
            # 6. 查询未完成的待办事项（应该不包含已放弃的）
            print("\n6. 查询未完成的待办事项（应该不包含已放弃的）...")
            response = requests.get(f"{BASE_URL}/todolist?status=未完成")
            pending_todos = json.loads(response.text)
            print(f"未完成待办事项数量: {len(pending_todos)}")
            
            abandoned_in_pending = any(todo['id'] == test_id for todo in pending_todos)
            print(f"已放弃的项目是否在未完成列表中: {'是' if abandoned_in_pending else '否'}")
            
        else:
            print("没有找到待办事项")
            
    except requests.exceptions.RequestException as e:
        print(f"请求错误: {e}")
    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {e}")

def test_error_handling():
    """测试错误处理"""
    print("\n=== 错误处理测试 ===")
    
    # 测试缺少todolist_id的情况
    print("测试缺少todolist_id参数...")
    try:
        response = requests.put(f"{BASE_URL}/todolist/abandon", json={})
        print(f"响应: {response.text}, 状态码: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"请求错误: {e}")

if __name__ == "__main__":
    test_abandon_feature()
    test_error_handling()
    print("\n测试完成！")