# Todo List 个人设置新增功能实现总结
## 新增实现功能的原因
在复现https://www.itpno.com/2133.html 的用FastGPT做一个Todolist时，发现原功能更多是面向程序员的开发友好型功能，而非用户导向的产品型功能，出于对数据库安全的维护，原代码仅支持todo条目的增改查，并以查和改的结合模拟删除功能，在这种情况下，如果用户想删除一项todo，实际要多走一步路径才可完成，同时也会有一些条件的限制（并非想改就改，必须用新的todo事项覆盖掉之前的旧内容）。因此我添加了放弃功能，并在此基础上衍生出还原功能。

## 新增实现的功能

### 1. 新增放弃接口

* **路由**: `PUT /todolist/abandon`
* **功能**: 将指定的待办事项标记为"已放弃"状态
* **请求参数**: `{"todolist_id": <待办事项ID>}`
* **自动记录**: 放弃时间会自动记录到 `abandon_time` 字段

### 2. 修改查询逻辑

* **默认查询**: `GET /todolist` 现在默认排除"已放弃"状态的项目
* **状态过滤**: 支持通过 `status` 参数查询特定状态
* **隔离显示**: "已放弃"的项目只在明确查询 `status=已放弃` 时显示

### 3. 新增还原接口

* **路由**: `PUT /todolist/restore`
* **功能**: 将指定的待办事项从"已放弃"状态还原为"未完成"
* **请求参数**: `{"todolist_id": <待办事项ID>}`
* **时间处理**: 还原时会清空 `do_time` 字段，表示重新进入未完成状态

## 核心代码变更

### 1. 新增 abandon\_todolist 函数

```python
@app.route('/todolist/abandon', methods=['PUT'])
def abandon_todolist():
    data = request.get_json()
    todolist_id = data.get("todolist_id")
    cursor = db.cursor()
    query = "UPDATE todolist SET status = %s, do_time = %s WHERE id = %s"
    cursor.execute(query, ("已放弃", datetime.now(), todolist_id))
    db.commit()
    return "Todolist abandoned successfully"
```

### 2. 修改 get\_todolist 函数

```python
@app.route('/todolist', methods=['GET'])
def get_todolist():
    status = request.args.get('status')
    cursor = db.cursor()
    if status is not None:
        cursor.execute("SELECT * FROM todolist WHERE status = %s", (status,))
    else:
        cursor.execute("SELECT * FROM todolist WHERE status != %s", ("已放弃",))
    todolist = cursor.fetchall()
    return todo_json(todolist)
```

### 3. 新增 restore\_todolist 函数

```python
@app.route('/todolist/restore', methods=['PUT'])
def restore_todolist():
    data = request.get_json()
    todolist_id = data.get("todolist_id")
    cursor = db.cursor()
    query = "UPDATE todolist SET status = %s, do_time = NULL WHERE id = %s"
    cursor.execute(query, ("未完成", todolist_id))
    db.commit()
    return "Todolist restored successfully"
```

## 状态管理

### 状态值定义

* `未完成`: 新创建或进行中的待办事项
* `已完成`: 已经完成的待办事项
* `已放弃`: 用户主动放弃的待办事项

### 查询行为

| 查询参数         | 返回结果          |
| ------------ | ------------- |
| 无参数          | 所有非"已放弃"状态的项目 |
| `status=未完成` | 只返回未完成的项目     |
| `status=已完成` | 只返回已完成的项目     |
| `status=已放弃` | 只返回已放弃的项目     |

### 状态转换

* 放弃操作：`未完成/已完成 → 已放弃`
* 还原操作：`已放弃 → 未完成`

## 使用方法

### 1. 启动应用

```bash
python3 todo_app.py
```

### 2. 放弃待办事项

```bash
curl -X PUT http://localhost:5000/todolist/abandon \
  -H "Content-Type: application/json" \
  -d '{"todolist_id": 1}'
```

### 3. 还原已放弃的待办事项

```bash
curl -X PUT http://localhost:5000/todolist/restore \
  -H "Content-Type: application/json" \
  -d '{"todolist_id": 1}'
```

### 4. 查询不同状态的待办事项

```bash
# 查询活跃项目（排除已放弃）
curl http://localhost:5000/todolist

# 查询已放弃的项目
curl http://localhost:5000/todolist?status=已放弃

# 查询已完成的项目
curl http://localhost:5000/todolist?status=已完成
```

## 测试

运行测试脚本验证功能：

```bash
# 确保Flask应用正在运行，然后执行：
python3 test_abandon_feature.py
```

## 注意事项

1. **数据一致性**: 被放弃的待办事项仍保留在数据库中，只是状态改变
2. **时间记录**: 放弃操作会自动记录当前时间到 `abandon_time` 字段
3. **还原逻辑**: 还原操作会清空 `abandon_time` 字段，状态回到 `未完成`
4. **查询隔离**: 默认查询不显示已放弃项目，需要明确指定才能查看
5. **错误处理**: 缺少必要参数时返回400错误码和错误信息

## 文件结构

```
/workspace/
├── todo_app.py              # 主应用文件（包含新功能）
├── requirements.txt         # Python依赖
├── README.md                # 使用说明
├── test_abandon_feature.py # 放弃功能测试脚本
├── test_restore_feature.py # 还原功能测试脚本
└── IMPLEMENTATION_SUMMARY.md # 本文件

