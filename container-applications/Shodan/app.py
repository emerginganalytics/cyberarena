from flask import Flask, redirect
from globals import ds_client, logger
from globals import populate_datastore
from ShodanApp.routes import shodan_app

app = Flask(__name__, template_folder='email_templates')

# Register Blueprint
app.register_blueprint(shodan_app)


@app.route('/<workout_id>')
def loader(workout_id):
    key = ds_client.key('cybergym-workout', workout_id)
    workout = ds_client.get(key)

    if workout:
        if workout['type'] == 'shodan':
            data = populate_datastore(workout_id=workout_id)
            logger.info(data)
            return redirect(f'/shodan_lite/{workout_id}')
        else:
            return redirect(f'/shodan_lite/invalid/{workout_id}')
    else:
        return redirect(f'/shodan_lite/invalid/{workout_id}')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
