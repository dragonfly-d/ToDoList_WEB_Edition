from flask import Flask, render_template
from data import db_session
from data.users import User
from data.tasks import Tasks

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


@app.route('/')
def test_page():
    db_sess = db_session.create_session()
    user_name = db_sess.query(User.name).filter(User.id == 7).first()
    return render_template('base.html', title='Test',
                           user_name=str(user_name)[2:-3])


@app.route('/main')
def main_page():
    db_sess = db_session.create_session()
    user_name = db_sess.query(User.name).filter(User.id == 7).first()
    tasks = db_sess.query(Tasks).all()
    return render_template('main.html', title='Test',
                           user_name=str(user_name)[2:-3], tasks=tasks)


@app.route('/main/today')
def Today_task_page():
    # Код, фильтрующий таски на сегодня должен быть заместо того, что стоит ниже
    db_sess = db_session.create_session()
    user_name = db_sess.query(User.name).filter(User.id == 7).first()
    tasks = db_sess.query(Tasks).all()
    return render_template('main.html', Today=True, All=False,
                           user_name=str(user_name)[2:-3], tasks=tasks,
                           list_name='Today Tasks')


@app.route('/main/all')
def All_task_page():
    # Код, фильтрующий все таски должен быть заместо того, что стоит ниже
    db_sess = db_session.create_session()
    user_name = db_sess.query(User.name).filter(User.id == 7).first()
    tasks = db_sess.query(Tasks).filter(Tasks.user_id == 7).all()
    return render_template('main.html', All=True, Today=False,
                           user_name=str(user_name)[2:-3], tasks=tasks,
                           list_name='All Tasks')


if __name__ == '__main__':
    db_session.global_init("db/TDLDataBase.db")
    app.run(port=8080, host='127.0.0.1', debug=True)
