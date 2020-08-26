#This file is for debugging purposes
#Run this file to verify that environment variables are set correctly

import os

print('Credentials from environ: {}'.format(os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')))
