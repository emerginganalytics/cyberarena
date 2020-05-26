from flask import Flask, render_template, redirect, flash, request, session, abort
import os

app = Flask(__name__)


@app.route('/')
def home():
    if not session.get('logged_in'):
        return render_template('index.html')
    else:
        return render_template('flag.html')


@app.route("/login", methods=["GET", "POST"])
def do_admin_login():
    if request.form['psw'] == 'cyberSecret42' and request.form['username'] == 'admin':
        session['logged_in'] = True
    else:
        flash('Incorrect Password')
    return home()


@app.route("/flag", methods=["POST"])
def flag():
    return render_template('flag.html')


@app.route("/logout", methods=["GET", "POST"])
def logout():
    session['logged_in'] = False
    return home()


@app.route("/workouts", methods=["POST"])
def workouts():
    session['logged_in'] = True
    return render_template('workouts.html')


if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True, host='0.0.0.0', port=4000)

