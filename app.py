import json
import sqlite3

from flask import Flask, jsonify, request, Response

app = Flask(__name__)

todos = [{
    "id": 1,
    "title": 'todo1',
    "completed": True
}, {
    "id": 2,
    "title": 'todo2',
    "completed": False
}]

conn = sqlite3.connect(r"todos.db", check_same_thread=False)
c = conn.cursor()
c.execute(
    """
    CREATE TABLE IF NOT EXISTS todos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title text,
        completed bool
    )
    """
)
conn.commit()
c.close()


def to_response(data, message, code):
    response = {
        "result": data,
        "error": None,
        "message": message
    }
    return Response(json.dumps(response), status=code, mimetype="application/json")


def to_error_response(error, message, code=500):
    response = {
        "result": None,
        "error": error,
        "message": message
    }
    return Response(json.dumps(response), status=code, mimetype="application/json")


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/api/v1/todos', methods=['GET'])
def get_todo_list():
    c1 = conn.cursor()
    query = "select * from todos"
    c1.execute(query)
    results = c1.fetchall()
    todo_list = []
    for result in results:
        todo_list.append({
            "id": result[0],
            "title": result[1],
            "completed": result[2]
        })
    return to_response(todo_list, "todo list loaded", 200)


@app.route('/api/v1/todos/<int:id>', methods=['GET'])
def get_todo_by_id(id):
    try:
        c1 = conn.cursor()
        query = "select * from todos1 where id = :id"
        c1.execute(query, {"id": id})
        result = c1.fetchone()
        founded_todo = {
            "id": result[0],
            "title": result[1],
            "completed": result[2]
        }
        return to_response(founded_todo, "todo loaded", 200)
    except sqlite3.Error as err:
        return to_error_response(' '.join(err.args), "", 500)


@app.route('/api/v1/todos', methods=['POST'])
def create_todo():
    if type(request.json["completed"]) != type(bool):
        return to_error_response("completed must be bool", "invalid input format", 400)

    try:
        query = "insert into todos ('title', 'completed') values (:title, :completed)"
        c1 = conn.cursor()
        c1.execute(query, {"title": request.json["title"], "completed": request.json["completed"]})
        conn.commit()

        return get_todo_by_id(c1.lastrowid)
    except sqlite3.Error as err:
        return to_error_response(' '.join(err.args), "", 500)


@app.route('/api/v1/todos/<int:id>', methods=['PUT'])
def update_todo_by_id(id):
    query = "update todos set 'title' = :title, 'completed' = :completed where id= :id"
    c1 = conn.cursor()
    c1.execute(query, {
        "title": request.json["title"],
        "completed": request.json["completed"],
        "id": id
    })
    conn.commit()
    return get_todo_by_id(id)


@app.route('/api/v1/todos/<int:id>', methods=['DELETE'])
def delete_todo_by_id(id):
    return str(id)


if __name__ == '__main__':
    app.run()
