#!/usr/bin/env python3
"""
测试恢复待办事项功能的示例脚本
注意：这个脚本需要在Flask应用运行时执行
"""

import requests
import json
from datetime import datetime

# 服务器地址
BASE_URL = "http://localhost:5000"

def test_restore_feature():
    """测试恢复功能"""

    print("=== Todo List 恢复功能测试 ===\n")

    # 1. 创建一个测试待办事项
    print("1. 创建测试待办事项...")
    create_data = {
        "todo": "测试待办事项 - 将被放弃再恢复",
        "status": "未完成",
        "todo_time": "2024-12-21 10:00:00",
        "created_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    try:
        response = requests.post(f"{BASE_URL}/todolist", json=create_data)
        print(f"创建结果: {response.text}")
    except requests.exceptions.ConnectionError:
        print("错误: 无法连接到服务器，请确保Flask应用正在运行")
        return

    # 2. 查询所有待办事项（获取刚创建的ID）
    print("\n2. 查询所有待办事项...")
    try:
        response = requests.get(f"{BASE_URL}/todolist/all")
        todos = json.loads(response.text)
        print(f"当前待办事项数量: {len(todos)}")

        if todos:
            test_id = todos[-1]['id']
            print(f"测试用待办事项ID: {test_id}")

            # 3. 先放弃这个待办事项
            print(f"\n3. 放弃待办事项 ID: {test_id}...")
            abandon_data = {"todolist_id": test_id}
            response = requests.put(f"{BASE_URL}/todolist/abandon", json=abandon_data)
            print(f"放弃结果: {response.text}")

            # 4. 确认已放弃状态
            print("\n4. 确认该待办事项出现在已放弃列表...")
            response = requests.get(f"{BASE_URL}/todolist?status=已放弃")
            abandoned_todos = json.loads(response.text)
            abandoned_ids = [todo['id'] for todo in abandoned_todos]
            print(f"已放弃任务ID列表: {abandoned_ids}")

            # 5. 恢复该待办事项
            print(f"\n5. 恢复待办事项 ID: {test_id}...")
            restore_data = {"todolist_id": test_id, "status": "未完成"}
            response = requests.put(f"{BASE_URL}/todolist/restore", json=restore_data)
            print(f"恢复结果: {response.text}")

            # 6. 确认该待办事项已不在已放弃列表
            print("\n6. 确认该待办事项已从已放弃列表中移除...")
            response = requests.get(f"{BASE_URL}/todolist?status=已放弃")
            abandoned_todos_after = json.loads(response.text)
            still_abandoned = any(todo['id'] == test_id for todo in abandoned_todos_after)
            print(f"该任务是否仍在已放弃列表中: {'是' if still_abandoned else '否'}")

            # 7. 确认该待办事项已出现在未完成列表
            print("\n7. 确认该待办事项已出现在未完成列表...")
            response = requests.get(f"{BASE_URL}/todolist?status=未完成")
            pending_todos = json.loads(response.text)
            restored_in_pending = any(todo['id'] == test_id for todo in pending_todos)
            print(f"该任务是否在未完成列表中: {'是' if restored_in_pending else '否'}")

        else:
            print("没有找到待办事项")

    except requests.exceptions.RequestException as e:
        print(f"请求错误: {e}")
    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {e}")

def test_restore_error_handling():
    """测试恢复功能错误处理"""
    print("\n=== 恢复功能错误处理测试 ===")

    print("测试缺少todolist_id参数...")
    try:
        response = requests.put(f"{BASE_URL}/todolist/restore", json={})
        print(f"响应: {response.text}, 状态码: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"请求错误: {e}")

if __name__ == "__main__":
    test_restore_feature()
    test_restore_error_handling()
    print("\n恢复功能测试完成！")
