from flask import Flask
from server_scripts import SHODAN_API_KEY

app = Flask(__name__, template_folder='templates')
import routes
import os

if __name__ == '__main__':
    os.environ['SHODAN_API_KEY'] = SHODAN_API_KEY
    app.run(host='0.0.0.0', port=5000)
