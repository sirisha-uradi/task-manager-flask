from flask import Flask, request, redirect, render_template_string
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

EDIT_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Edit Task</title>
    <style>
        body { font-family: 'Segoe UI', Arial, sans-serif; max-width: 500px; margin: 80px auto; }
        input[type=text] { width: 100%; padding: 12px; font-size: 15px; border: 1px solid #cbd5e0; border-radius: 8px; }
        button { margin-top: 15px; padding: 10px 18px; background: #4c51bf; color: white; border: none; border-radius: 8px; cursor: pointer; }
        a { display: block; margin-top: 15px; color: #718096; text-decoration: none; }
    </style>
</head>
<body>
    <h2>Edit Task</h2>
    <form method="POST">
        <input type="text" name="task_name" value="{{ task.task_name }}" required>
        <button type="submit">Save Changes</button>
    </form>
    <a href="/">← Cancel and go back</a>
</body>
</html>
"""
PAGE_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Task Manager</title>
    <style>
        * { box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            max-width: 600px;
            margin: 50px auto;
            background: #f4f6f8;
            color: #222;
        }
        h1 {
            text-align: center;
            color: #2d3748;
            margin-bottom: 25px;
        }
        form {
            display: flex;
            gap: 10px;
            margin-bottom: 25px;
        }
        input[type=text] {
            flex: 1;
            padding: 12px;
            border: 1px solid #cbd5e0;
            border-radius: 8px;
            font-size: 15px;
        }
        button {
            padding: 12px 20px;
            background: #4c51bf;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 15px;
        }
        button:hover { background: #434190; }
        ul { list-style: none; padding: 0; }
        li {
            background: white;
            padding: 14px 18px;
            margin-bottom: 10px;
            border-radius: 8px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        }
        .completed { text-decoration: line-through; color: #a0aec0; }
        .actions a {
            margin-left: 12px;
            text-decoration: none;
            font-size: 14px;
        }
        .empty-msg {
            text-align: center;
            color: #a0aec0;
            margin-top: 30px;
        }
    </style>
</head>
<body>
    <h1>📝 My Task Manager</h1>
<p style="text-align:center; color:#718096; margin-top:-10px; margin-bottom:15px;">
    {{ pending_count }} pending · {{ completed_count }} completed
</p>
<p style="text-align:center; margin-bottom:25px;">
    <a href="/?filter=all" style="margin:0 10px; {{ 'font-weight:bold; color:#4c51bf;' if current_filter == 'all' else 'color:#718096;' }}">All</a>
    <a href="/?filter=pending" style="margin:0 10px; {{ 'font-weight:bold; color:#4c51bf;' if current_filter == 'pending' else 'color:#718096;' }}">Pending</a>
    <a href="/?filter=completed" style="margin:0 10px; {{ 'font-weight:bold; color:#4c51bf;' if current_filter == 'completed' else 'color:#718096;' }}">Completed</a>
</p>
    <form action="/add" method="POST">
    <input type="text" name="task_name" placeholder="What needs to be done?" required>
    <input type="date" name="due_date" style="padding:12px; border:1px solid #cbd5e0; border-radius:8px;">
    <select name="category" style="padding:12px; border:1px solid #cbd5e0; border-radius:8px;">
        <option value="General">General</option>
        <option value="Work">Work</option>
        <option value="Personal">Personal</option>
        <option value="Urgent">Urgent</option>
    </select>
    <button type="submit">Add</button>
</form>
    <ul>
        {% for task in tasks %}
            <li>
                <span class="{{ 'completed' if task.status == 'completed' else '' }}">
    {% if task.category %}
        <span style="background:#edf2f7; color:#4c51bf; font-size:11px; padding:3px 8px; border-radius:12px; margin-right:8px;">{{ task.category }}</span>
    {% endif %}
    {{ task.task_name }}
    {% if task.due_date %}
        <small style="color:#a0aec0;"> (due {{ task.due_date }})</small>
    {% endif %}
</span>
                <span class="actions">
    {% if task.status != 'completed' %}
        <a href="/complete/{{ task.id }}">✅ Complete</a>
    {% endif %}
    <a href="/edit/{{ task.id }}">✏️ Edit</a>
    <a href="/delete/{{ task.id }}">🗑️ Delete</a>
</span>
            </li>
        {% endfor %}
    </ul>
    {% if not tasks %}
        <p class="empty-msg">No tasks yet — add one above 👆</p>
    {% endif %}
</body>
</html>
"""

@app.route("/")
def index():
    filter_value = request.args.get("filter", "all")
    response = supabase.table("tasks").select("*").order("created_at", desc=True).execute()
    all_tasks = response.data
    pending_count = len([t for t in all_tasks if t["status"] != "completed"])
    completed_count = len([t for t in all_tasks if t["status"] == "completed"])

    if filter_value == "pending":
        tasks = [t for t in all_tasks if t["status"] != "completed"]
    elif filter_value == "completed":
        tasks = [t for t in all_tasks if t["status"] == "completed"]
    else:
        tasks = all_tasks

    return render_template_string(PAGE_TEMPLATE, tasks=tasks, pending_count=pending_count, completed_count=completed_count, current_filter=filter_value)
@app.route("/add", methods=["POST"])
def add_task():
    task_name = request.form.get("task_name", "").strip()
    due_date = request.form.get("due_date") or None
    category = request.form.get("category", "General")
    if task_name:
        supabase.table("tasks").insert({"task_name": task_name, "status": "pending", "due_date": due_date, "category": category}).execute()
    return redirect("/")

@app.route("/complete/<task_id>")
def complete_task(task_id):
    supabase.table("tasks").update({"status": "completed"}).eq("id", task_id).execute()
    return redirect("/")
@app.route("/edit/<task_id>", methods=["GET", "POST"])
def edit_task(task_id):
    if request.method == "POST":
        new_name = request.form.get("task_name", "").strip()
        if new_name:
            supabase.table("tasks").update({"task_name": new_name}).eq("id", task_id).execute()
        return redirect("/")
    else:
        response = supabase.table("tasks").select("*").eq("id", task_id).execute()
        task = response.data[0] if response.data else None
        return render_template_string(EDIT_TEMPLATE, task=task)

@app.route("/delete/<task_id>")
def delete_task(task_id):
    supabase.table("tasks").delete().eq("id", task_id).execute()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)