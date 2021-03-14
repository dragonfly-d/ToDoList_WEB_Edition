from flask import Flask, render_template
from data import db_session
from data.users import User
from data.tasks import Tasks

app = Flask(__name__)

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

    return render_template("index.html", title="Your Current Tasks", tasks=tasks)


if __name__ == '__main__':
    main()
