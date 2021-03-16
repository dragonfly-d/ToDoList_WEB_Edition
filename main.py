from flask import Flask, render_template
from data import db_session
from data.users import User

app = Flask(__name__)


@app.route('/')
def test_page():
    db_sess = db_session.create_session()
    user_name = db_sess.query(User.name).filter(User.id == 4).first()
    return render_template('base.html', title='Test', user_name=str(user_name)[2:-3])


if __name__ == '__main__':
    db_session.global_init("db/TDLDataBase.db")
    app.run(port=8080, host='127.0.0.1', debug=True)
