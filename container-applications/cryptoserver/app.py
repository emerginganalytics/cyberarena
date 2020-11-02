from flask import Flask
app = Flask(__name__)
from routes import *


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
