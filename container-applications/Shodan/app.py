from flask import Flask

app = Flask(__name__, template_folder='templates')
SHODAN_API_KEY = '<YOUR_SHODAN_API_KEY>'
import routes
import os

if __name__ == '__main__':
    os.environ['SHODAN_API_KEY'] = '<YOUR_SHODAN_API_KEY>'
    app.run(host='0.0.0.0', port=5000)
