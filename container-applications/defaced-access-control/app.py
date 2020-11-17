from flask import Flask, render_template
import os

# application instance
app = Flask(__name__)
app.secret_key = os.urandom(12)


@app.route('/')
def home():
    page_template = 'index.html'
    return render_template(page_template)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=4000)
