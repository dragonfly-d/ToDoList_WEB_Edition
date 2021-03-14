from flask import Flask, render_template, redirect, abort, request
from data import db_session
from data.users import User
from data.tasks import Tasks
from forms.tasks import TasksForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

def main():
    db_session.global_init("db/TDLDataBase.db")
    app.run(port=8080, host='127.0.0.1', debug=True)


@app.route('/')
def index():
    return "Main page"

@app.route("/tasks", methods=["GET"])
def tasks():
    db_sess = db_session.create_session()
    tasks = db_sess.query(Tasks).all()

    return render_template("index.html", title="Today's Tasks", tasks=tasks)

@app.route('/add_tasks',  methods=['GET', 'POST'])
def add_tasks():
    form = TasksForm()

    if form.validate_on_submit():
        db_sess = db_session.create_session()

        tasks = Tasks()

        tasks.title = form.title.data
        tasks.done = form.done.data
        tasks.user_id = "" # Изменить после добавления функционала с пользователями
        db_sess.add(tasks)
        db_sess.commit()
        return redirect('/tasks')
    return render_template('add_task.html', title='Adding a task', form=form)

@app.route('/tasks/<int:task_id>',  methods=['GET', 'POST'])
def edit_tasks(task_id):
    form = TasksForm()

    if request.method == "GET":
        db_sess = db_session.create_session()
        tasks = db_sess.query(Tasks).filter(Tasks.id == task_id).first()

        if tasks:
            form.title.data = tasks.title
            form.done.data = tasks.done
        else:
            abort(404)

    if form.validate_on_submit():
        db_sess = db_session.create_session()
        tasks = db_sess.query(Tasks).filter(Tasks.id == task_id).first()

        if tasks:
            tasks.title = form.title.data
            tasks.done = form.done.data
            db_sess.commit()
            return redirect("/tasks")
        else:
            abort(404)
            
    return render_template('add_task.html', title='Editing a task', form=form)


if __name__ == '__main__':
    main()
