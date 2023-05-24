import os

from main_app_utilities.lms.lms_canvas import LMSCanvas


__author__ = "Philip Huff"
__copyright__ = "Copyright 2023, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Production"


if __name__ == "__main__":
    print(f"LMS Tester.")
    creds = os.environ.get('LMS_CREDENTIALS', None)
    if not creds:
        creds = str(input(f"What is the LMS API Key? "))
    url = os.environ.get('LMS_URL', None)
    if not url:
        url = str(input(f"What is the LMS URL? "))
    course_code = os.environ.get('LMS_COURSE', None)
    if not course_code:
        course_code = str(input(f"What is the LMS Course Code? "))

    lms = None
    lms_selection = str(input(f"Which LMS do you want to test: [C]anvas or [B]lackboard? [C] "))
    if not lms_selection or lms_selection .upper()[0] == "C":
        lms = LMSCanvas(url=url, api_key=creds, course_code=int(course_code))

    while True:
        action = str(input(f"What action are you wanting to test [G]et students, [Q]uit? [Q] "))
        if not action or action.upper()[0] == "Q":
            break
        if action.upper()[0] == "G":
            class_list = lms.get_class_list()
            print(class_list)
