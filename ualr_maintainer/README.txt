To launch the APP, you need a google cloud auth API key, you can create it within that page :
https://console.cloud.google.com/apis/credentials/serviceaccountkey?
Just select the project you want to access and create the JSON file, then put it in the root of this project's directory.

Before launching the app, you have to set up the the Goole API environment variable
    - Windows : set GOOGLE_APPLICATION_CREDENTIALS=[PATH TO CREDENTIALS.JSON]
    - Mac/Linux : export GOOGLE_APPLICATION_CREDENTIALS=[PATH TO CREDENTIALS.JSON]

Packages to install in our python venv :
    - flask
    - google api client 

Run python app.py

--------------------------------------------------------------------------------------------------------------------------------

RUN 

# dos example
To create a whole workshop, just run the create_dos_workout() method inside the 
create_workshop.py. It will fisrt create a specific network and the instanciate
the needed VM for the workshop.

# flask APP
Just run "flask run"

If you want to run it in debug mode :
set/export FLASK_ENV=development

--------------------------------------------------------------------------------------------------------------------------------

To create a instance for your google cloud project, you also need a bucket and custom images references (if needed)
    - images for ualr-cybersecurity : https://console.cloud.google.com/compute/images?project=...

