from google.cloud import storage

project_id = os.environ['GCLOUD_PROJECT']
CLOUD_STORAGE_BUCKET = "%s.appspot.com" % project_id

@app.route('/start_serving/<file_name>')
def start(file_name):
    gcs = storage.Client()
    bucket = gcs.get_bucket(CLOUD_STORAGE_BUCKET)
    blob = bucket.blob(file_name)
    return blob.download_as_string()