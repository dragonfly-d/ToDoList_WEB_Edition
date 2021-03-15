from flask import Flask, render_template, redirect,  url_for, request, abort, jsonify, make_response, Markup
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from data import db_session
from data.users import User
from data.tasks import Tasks
from forms.tasks import TasksForm
from forms.login import LoginForm
from forms.register import RegisterForm


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)

# Инициализируем декоратор авторизации. 
# Пользователь не сможет совершать действия, помеченные декоратором, если он не авторизован
@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)

def main():
    db_session.global_init("db/TDLDataBase.db")
    app.run(port=8080, host='127.0.0.1', debug=True)

'''
Надо будет добавить главную страницу, на которой пользователю будет предложено авторизоваться
Или сделать navbar, на котором будет отображаться статус авторизации
'''

@app.route('/')
def index():
    return render_template("main.html", title="Welcome!")

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()

        # Проверяем если пользователь зарегистрирован в базе данных и пароли совпадают
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/tasks")
        return render_template('login.html',
                               message="Incorrect email or password",
                               form=form)
    return render_template('login.html', title='Authorization', form=form)

@app.route("/register", methods=["GET", "POST"])
def registration():
    form = RegisterForm()

    if form.validate_on_submit():
        # Проверяем если пароли в форме совпадают
        if form.password.data != form.password_again.data:
            return render_template("register.html", title="Registration", message="Passwords are different", form=form)

        db_sess = db_session.create_session()
        # Смотрим если почтовый адрес еще не занят
        if db_sess.query(User).filter(form.email.data == User.email).first():
            return render_template("register.html", title="Registration", 
                                    message="The email is already taken. Try to", link='login', form=form)

        user = User()
        user.email = form.email.data
        user.set_password(form.password.data)
        user.name = form.name.data
        db_sess.add(user)
        db_sess.commit()
        return redirect("/login")
    return render_template("register.html", title="Registration", form=form)

@app.route("/logout", methods=["GET", "POST"])
def logout():
    logout_user()
    return redirect("/")

@app.route("/tasks", methods=["GET"])
@login_required
def tasks():
    db_sess = db_session.create_session()
    tasks = db_sess.query(Tasks).filter(Tasks.user_id == current_user.id).all() # Выводим только задачи, созданные этим пользователем

    return render_template("index.html", title="Today's Tasks", tasks=tasks)

@app.route('/add_tasks',  methods=['GET', 'POST'])
@login_required
def add_tasks():
    form = TasksForm()

    if form.validate_on_submit():
        db_sess = db_session.create_session()

        tasks = Tasks()

        tasks.title = form.title.data
        tasks.priority = form.priority.data
        tasks.scheduled_date = form.scheduled_date.data
        tasks.done = form.done.data
        tasks.user_id = current_user.id # Изменить после добавления функционала с пользователями
        db_sess.add(tasks)
        db_sess.commit()
        return redirect('/tasks')
    return render_template('add_task.html', title='Adding a task', form=form)

@app.route('/tasks/<int:task_id>',  methods=['GET', 'POST'])
@login_required
def edit_tasks(task_id):
    form = TasksForm()

    # Если пользователь получает данные, то заполням форму текующими данными о задаче
    if request.method == "GET":
        db_sess = db_session.create_session()
        tasks = db_sess.query(Tasks).filter(Tasks.id == task_id).first()

        if tasks:
            form.title.data = tasks.title
            form.priority.data = tasks.priority
            form.scheduled_date.data = tasks.scheduled_date
            form.done.data = tasks.done
        else:
            abort(404)

    # Если форма готова к отправке, обновляем информацию на более актульную
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        tasks = db_sess.query(Tasks).filter(Tasks.id == task_id).first()

        if tasks:
            tasks.title = form.title.data
            tasks.priority = form.priority.data
            tasks.scheduled_date = form.scheduled_date.data
            tasks.done = form.done.data
            db_sess.commit()
            return redirect("/tasks")
        else:
            abort(404)
            
    return render_template('add_task.html', title='Editing a task', form=form)

@app.route("/tasks_delete/<int:task_id>", methods=["GET", "POST"])
@login_required
def delete_task(task_id):
    db_sess = db_session.create_session()
    task = db_sess.query(Tasks).filter(Tasks.id == task_id).first()

    if task:
        db_sess.delete(task)
        db_sess.commit()
        return redirect("/tasks")
    else:
        abort(404)


if __name__ == '__main__':
    main()
