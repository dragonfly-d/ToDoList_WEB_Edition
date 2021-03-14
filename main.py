from flask import Flask, render_template
from data import db_session

app = Flask(__name__)


@app.route('/')
def test_page():
    return render_template('base.html', title='Test')


if __name__ == '__main__':
    db_session.global_init("db/TDLDataBase.db")
    app.run(port=8080, host='127.0.0.1', debug=True)
