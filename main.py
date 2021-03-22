from flask import Flask, render_template, redirect,  url_for, request, abort, jsonify, make_response, Markup
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from datetime import datetime, timedelta
from data import db_session
from data.users import User
from data.tasks import Tasks
from forms.tasks import TasksForm
from forms.login import LoginForm
from forms.register import RegisterForm
from itertools import groupby

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

login_manager = LoginManager()
login_manager.init_app(app)

# Инициализируем декоратор авторизации. 
# Пользователь не сможет совершать действия, помеченные декоратором, если он не авторизован
@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)

# Обработчик ошибки 404
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(401)
def page_not_found(e):
    return render_template('401.html'), 401

def main():
    db_session.global_init("db/TDLDataBase.db")
    app.run(port=8080, host='127.0.0.1', debug=True)

'''
Надо будет добавить главную страницу, на которой пользователю будет предложено авторизоваться
Или сделать navbar, на котором будет отображаться статус авторизации
'''

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect("/tasks/today")
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
            return redirect("/tasks/today")
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

@app.route("/tasks/today", methods=["GET"])
@login_required
def tasks():
    db_sess = db_session.create_session()
    # Запрашиваем только задачи, созданные этим пользователем и дата которых совпадает с сегодняшним днем
    today = datetime.strptime(f"{datetime.now().date()}", '%Y-%m-%d')
    tasks = db_sess.query(Tasks).filter(Tasks.user_id == current_user.id, Tasks.scheduled_date == today).all()
    tasks = sorted(tasks, key=lambda x: x.priority) # Сортируем задачи по приоритетности

    return render_template("main.html", title="Today's Tasks", tasks=tasks)

@app.route("/tasks/upcoming", methods=["GET"])
@login_required
def upcoming_tasks():
    db_sess = db_session.create_session()
    # Запрашиваем все задачи, добавленный этим пользователем
    tasks = db_sess.query(Tasks).filter(Tasks.user_id == current_user.id).all()
    
    # Сортируем и группируем задачи по дате
    data = {}
    for key, group in groupby(sorted(tasks, key=lambda x: x.scheduled_date), key=lambda x: x.scheduled_date):
        data[key] = sorted([thing for thing in group], key=lambda x: x.priority) # Сортируем задачи по приоритетности

    # Для того, чтобы правильно вывести задачи в таблицу посмотри циклы в templates/upcoming_tasks.html
    # Скорее всего придется делать новый template для правильного отображения
    return render_template('main.html', title="Upcoming Tasks", tasks=tasks) # tasks заменить на data

@app.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    db_sess = db_session.create_session()

    last_week_date = datetime.today() - timedelta(7) # Находим дату недельной давности 
    # Запрашиваем все выполненные этим пользователем задачи за последнюю неделю
    tasks = db_sess.query(Tasks).filter(Tasks.user_id == current_user.id, Tasks.done == 1, 
                                        last_week_date < Tasks.scheduled_date, Tasks.scheduled_date < datetime.now()).all()
    
    data = {"Monday": "", "Tuesday": "", "Wednesday": "", "Thursday": "", "Friday": "", "Saturday": "", "Sunday": ""}
    for key, group in groupby(sorted(tasks, key=lambda x: x.scheduled_date), key=lambda x: x.scheduled_date.strftime("%A")):
        data[key] = [val for val in group]

    # Запрашиваем завершенные задачи за все время
    tasks = db_sess.query(Tasks).filter(Tasks.user_id == current_user.id, Tasks.done == 1).all()
    completed = len(tasks)

    return render_template('dashboard.html', title="Upcoming Tasks", tasks=data, completed=completed)

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
        return redirect('/tasks/today')
    return render_template('add_task.html', title='Adding a task', form=form)

@app.route('/tasks/<int:task_id>',  methods=['GET', 'POST'])
@login_required
def edit_tasks(task_id):
    form = TasksForm()

    # Если пользователь получает данные, то заполням форму текующими данными о задаче
    if request.method == "GET":
        db_sess = db_session.create_session()
        tasks = db_sess.query(Tasks).filter(Tasks.id == task_id, Tasks.user_id == current_user.id).first()

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
            return redirect("/tasks/today")
        else:
            abort(404)
            
    return render_template('add_task.html', title='Editing a task', form=form)

@app.route("/tasks_delete/<int:task_id>", methods=["GET", "POST"])
@login_required
def delete_task(task_id):
    db_sess = db_session.create_session()
    task = db_sess.query(Tasks).filter(Tasks.id == task_id, Tasks.user_id == current_user.id).first()

    if task:
        db_sess.delete(task)
        db_sess.commit()
        return redirect("/tasks/today")
    else:
        abort(404)


if __name__ == '__main__':
    main()
