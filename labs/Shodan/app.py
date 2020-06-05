from flask import Flask

app = Flask(__name__, template_folder='templates')
SHODAN_API_KEY = 'zs72fHys8zo5n58zWOsHLJ8kLHOTBtWt'
import routes
import os
if __name__ == '__main__':
    os.environ['SHODAN_API_KEY'] = 'zs72fHys8zo5n58zWOsHLJ8kLHOTBtWt'
    app.run(host='0.0.0.0', port=5000)
