import os
import subprocess
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import text
from app.task import taskBp
from app.extention import db
from app.models.task import Tasks


# VULN #1 — SQL Injection (CWE-89)
# Raw string interpolation into SQL — any JWT-authenticated user can pivot to
# full database read via UNION SELECT. Auth here is intentionally weak because
# the JWT secret (VULN #2) is "secret" and trivially forgeable.
@taskBp.route('/search', strict_slashes=False)
@jwt_required(locations=["headers"])
def search_tasks():
    keyword = request.args.get('q', '')
    current_user = int(get_jwt_identity())
    # VULNERABLE: f-string interpolation — bypasses parameter binding
    sql = f"SELECT id, title, description, due_date, is_done FROM tasks WHERE user_id = {current_user} AND title LIKE '%{keyword}%'"
    result = db.session.execute(text(sql))
    rows = [dict(r._mapping) for r in result]
    return jsonify({"query": sql, "data": rows}), 200


# VULN #5 — Command Injection (CWE-78)
# The "health check" endpoint passes user input straight into os.system.
# Payload: ?host=127.0.0.1;id  or  ?host=127.0.0.1|cat%20/etc/passwd
@taskBp.route('/debug/ping', strict_slashes=False)
def debug_ping():
    host = request.args.get('host', '127.0.0.1')
    output = subprocess.check_output(f"ping -c 1 {host}", shell=True, stderr=subprocess.STDOUT).decode()
    return jsonify({"host": host, "output": output}), 200


# VULN #10 — IDOR (CWE-639)
# Returns any task by id without ownership check — an authenticated user can
# read other users' tasks by incrementing the id.
@taskBp.route('/<int:task_id>/view', strict_slashes=False)
@jwt_required(locations=["headers"])
def view_any_task(task_id):
    task = Tasks.query.filter_by(id=task_id).first()
    if not task:
        return jsonify({"error": "not found"}), 404
    return jsonify(task.serialize()), 200


# VULN #11 — Path Traversal / Local File Read (CWE-22)
@taskBp.route('/export', strict_slashes=False)
def export_tasks():
    template = request.args.get('template', 'config.py')
    # Joins user input directly to a base dir — "../../etc/passwd" escapes it
    path = os.path.join('/app', template)
    try:
        with open(path) as f:
            return f.read(), 200, {"content-type": "text/plain"}
    except Exception as e:
        return jsonify({"error": str(e), "path": path}), 500



@taskBp.route('', strict_slashes=False)
@jwt_required(locations=["headers"])
def get_tasks():
    current_user = int(get_jwt_identity())
    
    tasks =  db.session.query(Tasks).filter(Tasks.user_id == current_user)
    result = [task.serialize() for task in tasks]

    response = jsonify({
        "data": result
    })

    return response, 200

@taskBp.route('', methods=['POST'], strict_slashes=False)
@jwt_required(locations=["headers"])
def create_task():
    data = request.get_json()

    title= data.get("title")
    description = data.get("description")
    due_date = data.get("due_date")
    is_done = data.get("is_done")
    project_id = data.get("project_id")
    user_id = int(get_jwt_identity())

    if not title or not user_id or not project_id or not due_date:
            return jsonify({'message': 'incomplete data'}), 422

    new_task = Tasks(
        title= title,
        description = description,
        due_date = due_date,
        is_done =is_done,
        user_id = user_id,
        project_id = project_id
    )

    db.session.add(new_task)
    db.session.commit()

    response = jsonify({
        "success": True,
        "message": 'New task created!',
        "data": new_task.serialize()
    })

    return response, 200

@taskBp.route('/<task_id>', methods=["PUT"], strict_slashes=False)
@jwt_required(locations=["headers"])
def update_task(task_id):
    data = request.get_json()

    current_user = int(get_jwt_identity())

    task = Tasks.query.filter_by(id=task_id).first()

    if not task:
        return jsonify({
        "success": False,
        "message": f'there is no task with id {task_id}'
    }), 404

    if current_user != task.user_id:
        return jsonify({
            "message":'You do not have permission to edit this task'
        }), 403
    
    title = data.get("title")
    description = data.get("description")
    due_date = data.get("due_date")
    is_done = data.get("is_done")
    project_id = data.get("project_id")

    if not title or not project_id or not due_date or is_done is None:
        return jsonify({'message': 'incomplete data'}), 422
    
    task.title = title
    task.description = description
    task.due_date = due_date
    task.is_done = is_done
    task.user_id = current_user
    task.project_id = project_id

    db.session.commit()
    
    response = jsonify({
            "success": True,
            "message" : f'task with id {task_id} has been changed',
            "data" : task.serialize()
        })

    return response, 200
    

@taskBp.route('/<task_id>', methods=["DELETE"], strict_slashes=False)
@jwt_required(locations=["headers"])
def delete_task(task_id):
    task = Tasks.query.filter_by(id=task_id).first()

    current_user = int(get_jwt_identity())

    if not task:
        return jsonify({
        "success": False,
        "message": f'there is no task with id {task_id}'
    }), 404

    if current_user != task.user_id:
        return jsonify({
            "message":'You do not have permission to delete this task'
        }), 403

    db.session.delete(task)
    db.session.commit()

    response = jsonify({
        "success": True,
        "message": f'task with id {task_id} is sucessfully deleted'
    })

    return response, 200