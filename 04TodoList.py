from flask import Flask, request
import mysql.connector
from datetime import datetime
import json

app = Flask(__name__)

# 连接到 MySQL 数据库
db = mysql.connector.connect(
    host="localhost",
    port=3306,
    user="root",
    password="oneapimysql",
    database="fastgpt"
)


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        """
        这个方法提供了一种将 Python 对象序列化为 JSON 格式的方式。
        它检查对象是否为 datetime 类型，如果是，将其格式化为 ISO 8601 日期时间字符串。
        如果对象不是 datetime 类型，它调用父类的 default 方法。


        参数：
            obj (任何): 要序列化的 Python 对象

        返回：
            str 或 obj: 如果对象是 datetime，返回其 ISO 格式字符串；否则，返回父类 default 方法序列化后的结果。

        使用示例：
            >>> json_encoder = MyJSONEncoder()
            >>> import datetime
            >>> date_obj = datetime.date.today()
            >>> json_encoder.default(date_obj)
            '2024-01-18'
        """
        if isinstance(obj, datetime):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)


def todo_json(array):
    """
    将数组中的每个元素转换为字典，并添加到一个 JSON 格式的列表中。


    参数:
        array (list of tuples): 每个元组代表一个待办事项的数据，元组的索引对应字典中的键

    返回:
        str: JSON 格式的字符串，包含所有待办事项的字典

    使用示例:
        >>> array = [(1, '事项 1', 0, '2024-01-19 12:00:00', '2024-01-18 12:00:00', None)]
        >>> todo_json(array)
        '[{"id": 1, "todo": "事项 1", "status": 0, "todo_time": "2024-01-19 12:00:00", "created_time": "2024-01-18 12:00:00", "do_time": null}]'

    注意:
        元组中每个索引对应的详细信息应该是: [id, todo, status, todo_time, created_time, do_time]
        在实际编写代码时，确保数组中的元组结构与预期一致，并且键值对的排序也正确。
    """
    json_list = []
    for item in array:
        item_dict = {
            'id': item[0],
            'todo': item[1],
            'status': item[2],
            'todo_time': item[3],
            'created_time': item[4],
            'do_time': item[5],
            'abandon_time': item[6]
        }
        json_list.append(item_dict)
    # 将 JSON 对象转换为字符串
    json_str = json.dumps(json_list, cls=CustomJSONEncoder)
    return json_str


@app.route('/todolist', methods=['GET'])
def get_todolist():
    """
    这个函数用于从数据库中获取待办事项列表。它检查请求的查询字符串中是否存在 'status' 参数。
    如果存在 'status' 参数，函数将使用它来筛选数据库中的待办事项，只返回指定状态的事项。
    如果不存在 'status' 参数，将返回所有的待办事项。
    注意：当查询"已完成"或"未完成"状态时，不会显示"已放弃"的项目。


    返回:
        list: 一个 JSON 格式的待办事项列表。列表中的每个元素应该包含 'id', 'todo', 'status', 'todo_time', 和 'created_time' 字段。

    使用示例:
        >>> get_todolist()
        [{'id': 1, 'todo': '事项 1', 'status': '未完成', 'todo_time': '2024-01-19 12:00:00', 'created_time': '2024-01-18 12:00:00'}, {'id': 2, 'todo': '事项 2', 'status': '已完成', 'todo_time': '2024-01-19 15:00:00', 'created_time': '2024-01-18 15:00:00'}]

    注意:
        需要确保数据库连接 'db' 和游标对象 'cursor' 已经在调用此函数之前正确初始化。
    """
    # 从请求的查询字符串中获取 status 参数
    status = request.args.get('status')
    cursor = db.cursor()
    if status is not None:
        # 如果查询特定状态，直接按状态过滤
        cursor.execute("SELECT * FROM todolist WHERE status = %s", (status,))
    else:
        # 如果没有指定状态，返回所有非"已放弃"状态的项目
        cursor.execute("SELECT * FROM todolist WHERE status != '已放弃'")
    todolist = cursor.fetchall()
    return todo_json(todolist)


@app.route('/todolist/abandon', methods=['PUT'])
def abandon_todolist():
    """
    将指定的待办事项标记为"已放弃"状态。

    从客户端获取 JSON 数据，提取 todolist_id，然后将该待办事项的状态更新为"已放弃"，
    并记录放弃的时间。

    请求数据格式：
        {
            "todolist_id": 1
        }

    返回值：
        str：操作结果的描述，通常是一个成功消息。

    使用示例：
        >>> data = {'todolist_id': 1}
        >>> abandon_todolist()
        'Todolist abandoned successfully'

    注意事项：
        需要确保数据库连接 'db' 和游标对象 'cursor' 已经在调用此函数之前正确初始化。
        被标记为"已放弃"的待办事项在查询"已完成"或"未完成"时不会被显示。
    """
    data = request.get_json()
    todolist_id = data.get('todolist_id')

    if not todolist_id:
        return 'Missing todolist_id', 400

    # 获取当前时间作为放弃时间
    abandon_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    cursor = db.cursor()
    # 同时更新状态、完成时间和放弃时间
    query = "UPDATE todolist SET status = %s,  abandon_time = %s WHERE id = %s"
    cursor.execute(query, ('已放弃',  abandon_time, todolist_id))
    db.commit()

    return 'Todolist abandoned successfully'



@app.route('/todolist', methods=['POST'])
def create_todolist():
    """
    将新的待办事项添加到数据库中。


    这个函数从请求中获取 JSON 格式的数据，然后使用这些数据在数据库中创建一个新的待办事项条目。

    参数：
        无。

    返回：
        tuple：包含成功消息和状态码的元组。

    使用示例：
        >>> create_todolist()
        ('Todolist created successfully', 201)
    """
    data = request.get_json()
    cursor = db.cursor()
    query = "INSERT INTO todolist (todo, status, todo_time, created_time) VALUES (%s, %s, %s, %s)"
    cursor.execute(query, (data['todo'], data['status'], data['todo_time'], data['created_time']))
    db.commit()
    return 'Todolist created successfully', 201


@app.route('/todolist', methods=['PUT'])
def update_todolist():
    """
    从客户端获取 JSON 数据，提取 todolist_id、status 和 do_time 值，然后使用这些值更新数据库中的待办事项。


    返回值：
        str：操作结果的描述，通常是一个成功消息。

    使用示例：
        >>> data = {'todolist_id': 1, 'status': '完成', 'do_time': '2024-01-27 12:30:00'}
        >>> update_todolist()
        'Todolist updated successfully'

    注意事项：
        需要确保数据库连接 'db' 和游标对象 'cursor' 已经在调用此函数之前正确初始化。
        'request' 对象应该是来自 Flask 上下文的请求对象，以确保能够正确获取 JSON 数据。

    """
    data = request.get_json()
    # 从 JSON 数据中提取 status 和 do_time 值
    todolist_id = data.get('todolist_id')
    status = data.get('status')
    do_time = data.get('do_time')
    cursor = db.cursor()
    query = "UPDATE todolist SET status = %s, do_time = %s WHERE id = %s"
    cursor.execute(query, (status, do_time, todolist_id))
    db.commit()
    return 'Todolist updated successfully'


@app.route('/todolist/restore', methods=['PUT'])
def restore_todolist():
    """
    通用的任务恢复功能
    可以将任何任务恢复到指定状态，默认恢复为"未完成"
    """
    data = request.get_json()
    todolist_id = data.get('todolist_id')
    target_status = data.get('status', '未完成')  # 默认恢复为未完成

    if not todolist_id:
        return 'Missing todolist_id', 400

    cursor = db.cursor()

    # 根据目标状态进行不同的处理
    if target_status == '未完成':
        # 恢复为未完成，清空完成时间和放弃时间
        query = "UPDATE todolist SET status = %s, do_time = %s, abandon_time = %s WHERE id = %s"
        cursor.execute(query, (target_status, None, None, todolist_id))
    else:
        # 恢复为其他指定状态，只清除放弃时间
        query = "UPDATE todolist SET status = %s, abandon_time = %s WHERE id = %s"
        cursor.execute(query, (target_status, None, todolist_id))

    db.commit()
    return 'Todolist restored successfully'

@app.route('/todolist/all', methods=['GET'])
def get_all_todolist():
    """
    获取所有任务，包括已放弃的任务
    用于用户查看完整历史记录
    """
    cursor = db.cursor()
    cursor.execute("SELECT * FROM todolist")
    todolist = cursor.fetchall()
    return todo_json(todolist)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
