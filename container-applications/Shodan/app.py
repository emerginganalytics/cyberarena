import routes
import os

from flask import Flask

app = Flask(__name__, template_folder='templates')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
