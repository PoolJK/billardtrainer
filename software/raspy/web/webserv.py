from flask import Flask, render_template, request


class Webserver:
    """
    Simple web server with Flask
    Show some pages and react to form methods.
    Send form results via message queue.
    """

    def __init__(self, que):
        """
        Associate urls with handler functions.
        :param que: message queue to send form results to
        """
        self.repq = que
        self.wapp = Flask(__name__)
        self.wapp.add_url_rule('/', 'index', self.index, methods=['POST', 'GET'])

    def index(self):
        """
        Actions for index page request
        Handle post request
        :return: requested web page
        """
        if request.method == 'POST':
            action = request.form['Button1']
            #print(number)
            self.repq.put(action)
            return render_template('result.html', n=action)
        else:
            return render_template("index.html")

    def run(self):
        """
        Run flask
        """
        self.wapp.run()
