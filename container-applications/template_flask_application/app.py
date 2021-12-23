from flask import Flask, render_template, request, redirect, session
from google.cloud import datastore
from main_app import main_app

app = Flask(__name__)
app.register_blueprint(main_app, url_prefix="/app")
application_name = "<YOUR APPLICATION NAME GOES HERE>"


@app.route('/<workout_id>', methods=['GET', 'POST'])
def workout_entry(workout_id):
    ds_client = datastore.Client()
    workout = ds_client.get(ds_client.key('cybergym-workout', workout_id))
    if not workout or ('type' not in workout and workout['name'] != application_name):
        return render_template('invalid_workout.html')
    else:
        session['workout'] = workout
        return redirect(f"/app/{workout_id}")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
