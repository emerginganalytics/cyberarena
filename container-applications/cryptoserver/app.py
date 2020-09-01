from flask import Flask

app = Flask(__name__)

import routes
import os

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get(port=5000)))
