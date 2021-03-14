from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def test_page():
    return render_template('base.html', title='Test')

if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1', debug=True)
