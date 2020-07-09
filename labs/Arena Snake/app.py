from flask import Flask, render_template, request, jsonify
import os

# application instance
app = Flask(__name__)
app.secret_key = os.urandom(12)


@app.route('/arena_snake')
def arena_snake():
    page_template = 'arena_snake.html'
    return render_template(page_template)


@app.route('/snake_flag', methods=['POST'])
def login_sql():
    if request.method == 'POST':
        score = (request.json['score'])
        flag_data = {'flag': 'CyberGym{Arena_Snake_Champion}'}
        return jsonify(flag_data)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=4000)
