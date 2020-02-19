from flask import Flask, render_template, request
from queue import Queue

repq = None

wapp = Flask(__name__)


@wapp.route('/')
def index():
    return render_template("index.html")


@wapp.route('/', methods=['POST'])
def getvalue():
    if request.method == 'POST':
        number = request.form['Button1']
        print(number)
        repq.put(number)
        return render_template('result.html', n=number)


def websetup(que):
    global repq
    repq = que


if __name__ == "__main__":
    wapp.run(debug=True)
