from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# /// = relative path, //// = absolute path
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    complete = db.Column(db.Boolean)


@app.route("/", methods=["GET", "POST"])
def home():
    search_query = request.args.get('search')
    filter_status = request.args.get('filter')
    page = request.args.get('page', 1, type=int)
    per_page = 5  # Number of tasks per page

    query = Todo.query

    if search_query:
        query = query.filter(Todo.title.contains(search_query))

    if filter_status == "complete":
        query = query.filter_by(complete=True)
    elif filter_status == "incomplete":
        query = query.filter_by(complete=False)

    pagination = query.paginate(page=page, per_page=per_page)
    todo_list = pagination.items

    return render_template("base.html", todo_list=todo_list, pagination=pagination, search_query=search_query, filter_status=filter_status)


@app.route("/add", methods=["POST"])
def add():
    title = request.form.get("title")
    page = request.args.get('page', 1)
    new_todo = Todo(title=title, complete=False)
    db.session.add(new_todo)
    db.session.commit()
    return redirect(url_for("home", page=page))


@app.route("/update/<int:todo_id>")
def update(todo_id):
    todo = Todo.query.filter_by(id=todo_id).first()
    todo.complete = not todo.complete
    db.session.commit()
    page = request.args.get('page', 1)
    return redirect(url_for("home", page=page))


@app.route("/delete/<int:todo_id>")
def delete(todo_id):
    todo = Todo.query.filter_by(id=todo_id).first()
    db.session.delete(todo)
    db.session.commit()
    page = request.args.get('page', 1)
    return redirect(url_for("home", page=page))

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
