import shodan
import shodan.helpers as helpers
from flask import Blueprint, redirect, render_template, request
from globals import SHODAN_API_KEY, ds_client, logger

shodan_app = Blueprint(
    'shodan_app', __name__,
    url_prefix='/shodan_lite',
    template_folder='templates/',
    static_folder='static'
)


@shodan_app.route('/<workout_id>', methods=['GET', 'POST'])
def default(workout_id):
    api = shodan.Shodan(SHODAN_API_KEY)
    page_template = 'index.jinja'

    workout = ds_client.get(ds_client.key('cybergym-workout', workout_id))

    if workout:
        if workout['type'] == 'shodan':
            if request.method == 'POST':
                logger.info(f'POST to /{workout_id}')
                try:
                    query = request.form.get('shodan_query')
                    page_num = request.form.get('page_number')
                    result = api.search(query, limit=10)
                    result_count = api.count(query)
                    print(result.keys())

                    return render_template(
                        page_template,
                        shodanResults=result,
                        resultCount=result_count,
                        query=query,
                        page_num=page_num,
                        workoutid=workout_id,
                    )
                except shodan.APIError as e:
                    logger.info(e)
                    e_template = 'invalid_query.jinja'
                    return render_template(e_template)
            return render_template(page_template)
        else:
            return redirect(f'/invalid/{workout_id}')
    else:
        return redirect(f'/invalid/{workout_id}')


@shodan_app.route('/results/<string:ip>/<workout_id>')
def result(ip, workout_id):
    api = shodan.Shodan(SHODAN_API_KEY)
    workout = ds_client.get(ds_client.key('cybergym-workout', workout_id))

    if workout:
        if workout['type'] == 'shodan':

            ip_list = []
            ip_list.append(ip)
            info = api.host(ip_list, history=True)
            for tmp in info["data"]:
                has_screenshot = helpers.get_screenshot(tmp)
                if has_screenshot is not None:
                    info["screenshot"] = has_screenshot["data"]

            page_template = 'results.jinja'

            return render_template(page_template, resultInfo=info, workoutid=workout_id,)
        else:
            return redirect(f'/invalid/{workout_id}')
    else:
        return redirect(f'/invalid/{workout_id}')


@shodan_app.route('/data/<workout_id>', methods=['GET', 'POST'])
def data(workout_id):
    page_template = 'raw_data.jinja'
    workout = ds_client.get(ds_client.key('cybergym-workout', workout_id))

    if workout:
        if workout['type'] == 'shodan':
            if request.method == "POST":
                logger.info(f"POSTING to /data/{workout_id}")
                return render_template(page_template, rawData=request.form.get('data'), workoutid=workout_id,)
            if request.method == "GET":
                logger.info(f'GET /data/{workout_id}')
                print(type(request.get_data()))
        else:
            return redirect(f'/invalid/{workout_id}')
    else:
        return redirect(f'/invalid/{workout_id}')


@shodan_app.route('/query/<string:query>/<int:page>/<workout_id>')
def view_all_query_results(query, page, workout_id):
    api = shodan.Shodan(SHODAN_API_KEY)
    workout = ds_client.get(ds_client.key('cybergy-workout', workout_id))

    if workout:
        if workout['type'] == 'shodan':
            if request.method == "POST":
                result = api.search(query, page=page)
        else:
            return redirect(f'/invalid/{workout_id}')
    else:
        return redirect(f'/invalid/{workout_id}')


@shodan_app.route('/invalid/<workout_id>')
def invalid(workout_id):
    page_template = 'invalid_workout.html'
    logger.error(f'/invalid/{workout_id}')
    return render_template(page_template)
