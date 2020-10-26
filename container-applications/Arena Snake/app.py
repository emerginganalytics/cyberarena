from flask import Flask, render_template, request, jsonify, redirect
from google.cloud import datastore, runtimeconfig
import os

# application instance
app = Flask(__name__)
app.secret_key = os.urandom(12)

ds_client = datastore.Client()
runtimeconfig_client = runtimeconfig.Client()
myconfig = runtimeconfig_client.config('cybergym')
project = myconfig.get_variable('project').value.decode("utf-8")
dns_suffix = myconfig.get_variable('dns_suffix').value.decode("utf-8")


@app.route('/loader/<workout_id>')
def loader(workout_id):
    key = ds_client.key('cybergym-workout', workout_id)
    workout = ds_client.get(key)

    if workout:
        if workout['type'] == 'arena_snake':
            return redirect('/arena_snake/' + workout_id)
    else:
        return redirect(404)


@app.route('/arena_snake/<workout_id>')
def arena_snake(workout_id):
    key = ds_client.key('cybergym-workout', workout_id)
    workout = ds_client.get(key)
    if workout['type'] == 'arena_snake':
        page_template = 'arena_snake.html'
        return render_template(page_template, workout_id=workout_id)
    else:
        return redirect(404)


@app.route('/snake_flag', methods=['POST'])
def snake_flag():
    if request.method == 'POST':
        score = (request.json['score'])
        flag_data = {'flag': 'CyberGym{Arena_Snake_Champion}'}
        return jsonify(flag_data)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=4000)
