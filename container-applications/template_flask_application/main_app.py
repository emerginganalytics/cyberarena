from flask import Blueprint, render_template, request, redirect, session
from google.cloud import datastore
# Add your imports from the utilities folder here

# Rename main_app to your application in both places
main_app = Blueprint("main_app", __name__, static_folder="static", template_folder="template", url_prefix="/app")

ds_client = datastore.Client()


@main_app.route('/<workout_id>', methods=['GET', 'POST'])
def app_entry(workout_id):
    workout = ds_client.get(ds_client.key('cybergym-workout', workout_id))
    if not workout:
        return render_template('invalid_workout.html')

    if request.method == 'POST':
        #DO SOMETHING
        return redirect(f'/app/<SOME ROUTE>/{workout_id}')
    page_template = "SOME_TEMPLATE.html"
    return render_template(page_template)
