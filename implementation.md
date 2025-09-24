## Todo List API 使用说明

### 新增功能1：已放弃状态、撤销状态

#### 功能描述

新增了"已放弃"功能，允许用户将待办事项标记为已放弃状态。被标记为"已放弃"的待办事项在查询"已完成"或"未完成"状态时不会被显示。
实现细节：在数据库中会将字段 `status` 更新为 `"已放弃"`，并将 `abandon_time` 字段设置为当前时间；该字段在返回 JSON 时会序列化为 ISO8601 格式。


### 新增功能2：撤销状态

#### 功能描述

新增了"撤销"功能，允许用户将已放弃或其他状态的待办事项撤销回“未完成”状态。被标记为"撤销"的待办事项会重新出现在“未完成”列表中。
实现细节：在数据库中将字段 `status` 更新为 `"未完成"`，同时清空 `abandon_time` 字段（如果原状态是“已放弃”），确保撤销操作在返回 JSON 时正常序列化为 ISO8601 格式。


---

### API 接口

#### 1. 放弃待办事项

* **URL**: `/todolist/abandon`
* **方法**: PUT
* **请求体**:

```json
{
    "todolist_id": 1
}
```

* **响应**: "Todolist abandoned successfully"
  实现细节：对应的 SQL 更新语句为：

```sql
UPDATE todolist SET status = '已放弃', abandon_time = NOW() WHERE id = <id>;
```

---

#### 2. 恢复待办事项

* **URL**: `/todolist/restore`
* **方法**: PUT
* **请求体**:

```json
{
    "todolist_id": 1,
    "status": "未完成"  // 可选，默认为"未完成"
}
```

* **响应**: "Todolist restored successfully"
  实现细节：恢复时会将 `status` 更新为 `"未完成"`（或指定值），并将 `abandon_time` 字段置为 `NULL`：

```sql
UPDATE todolist SET status = '未完成', abandon_time = NULL WHERE id = <id>;
```

---

#### 3. 查询待办事项

* **URL**: `/todolist`
* **方法**: GET
* **查询参数**:

  * `status` (可选): 待办事项状态（未完成/已完成/已放弃）

实现细节：

* 如果指定了 `status` 参数，则执行：

```sql
SELECT * FROM todolist WHERE status = '<status>';
```

* 如果未指定 `status` 参数，则默认应排除已放弃：

```sql
SELECT * FROM todolist WHERE status != '已放弃';
```

（现有代码返回全部数据，包括已放弃，需要修改以符合此逻辑）

---

#### 4. 查询所有待办事项

* **URL**: `/todolist/all`
* **方法**: GET
* **说明**: 返回所有待办事项，包括已放弃的任务

实现细节：SQL 示例：

```sql
SELECT * FROM todolist;
```

---

### 行为变化:

* 当不指定 `status` 参数时，只返回非"已放弃"状态的待办事项
* 当指定 `status=已完成` 时，只返回已完成的待办事项（不包括已放弃）
* 当指定 `status=未完成` 时，只返回未完成的待办事项（不包括已放弃）
* 当指定 `status=已放弃` 时，只返回已放弃的待办事项

实现细节：当前源码默认查询会返回所有状态（包括已放弃），需要在逻辑中增加 `status != '已放弃'` 才能符合以上行为。

> 注意：根据现有代码，**不支持** `include_abandoned` 查询参数。需要获取所有任务（包括已放弃）时应使用 `/todolist/all` 接口。

---

### 使用示例

#### 放弃一个待办事项

```bash
curl -X PUT http://localhost:5000/todolist/abandon \
  -H "Content-Type: application/json" \
  -d '{"todolist_id": 1}'
```

#### 恢复一个已放弃的待办事项

```bash
curl -X PUT http://localhost:5000/todolist/restore \
  -H "Content-Type: application/json" \
  -d '{"todolist_id": 1, "status": "未完成"}'
```

#### 查询所有活跃的待办事项（排除已放弃）

```bash
curl http://localhost:5000/todolist
```

#### 查询所有待办事项（包括已放弃）

```bash
curl http://localhost:5000/todolist/all
```

#### 查询已放弃的待办事项

```bash
curl http://localhost:5000/todolist?status=已放弃
```

#### 查询已完成的待办事项（不包括已放弃）

```bash
curl http://localhost:5000/todolist?status=已完成
```

---

### 数据库状态值

* **未完成**: 待办事项尚未完成
* **已完成**: 待办事项已完成
* **已放弃**: 待办事项已被放弃

实现细节：状态值以字符串形式保存在 `status` 字段中，与 API 查询参数保持一致。

---

### 注意事项

* 被标记为"已放弃"的待办事项会记录放弃时间到 `abandon_time` 字段
* 在默认查询（不指定status）时，已放弃的项目不会显示
* 只有明确查询 `status=已放弃` 时才会显示已放弃的项目
* 恢复功能可以将任务恢复到任意状态，默认恢复为"未完成"状态
* `/todolist/all` 接口提供完整的任务历史视图，便于用户查看所有任务包括已放弃的任务


