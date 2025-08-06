# Todo List API 使用说明

## 新增功能：已放弃状态

### 功能描述
新增了"已放弃"功能，允许用户将待办事项标记为已放弃状态。被标记为"已放弃"的待办事项在查询"已完成"或"未完成"状态时不会被显示。

### API 接口

#### 1. 放弃待办事项
- **URL**: `/todolist/abandon`
- **方法**: `PUT`
- **请求体**:
```json
{
    "todolist_id": 1
}
```
- **响应**: `"Todolist abandoned successfully"`

#### 2. 查询待办事项（已修改）
- **URL**: `/todolist`
- **方法**: `GET`
- **查询参数**: 
  - `status` (可选): 待办事项状态

**行为变化**:
- 当不指定 `status` 参数时，只返回非"已放弃"状态的待办事项
- 当指定 `status=已完成` 时，只返回已完成的待办事项（不包括已放弃）
- 当指定 `status=未完成` 时，只返回未完成的待办事项（不包括已放弃）
- 当指定 `status=已放弃` 时，只返回已放弃的待办事项

### 使用示例

#### 放弃一个待办事项
```bash
curl -X PUT http://localhost:5000/todolist/abandon \
  -H "Content-Type: application/json" \
  -d '{"todolist_id": 1}'
```

#### 查询所有活跃的待办事项（排除已放弃）
```bash
curl http://localhost:5000/todolist
```

#### 查询已放弃的待办事项
```bash
curl http://localhost:5000/todolist?status=已放弃
```

#### 查询已完成的待办事项（不包括已放弃）
```bash
curl http://localhost:5000/todolist?status=已完成
```

### 数据库状态值
- `未完成`: 待办事项尚未完成
- `已完成`: 待办事项已完成
- `已放弃`: 待办事项已被放弃

### 注意事项
1. 被标记为"已放弃"的待办事项会记录放弃时间到 `do_time` 字段
2. 在默认查询（不指定status）时，已放弃的项目不会显示
3. 只有明确查询 `status=已放弃` 时才会显示已放弃的项目