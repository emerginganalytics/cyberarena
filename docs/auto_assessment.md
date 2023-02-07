# Automated Assessment for Cyber Arena Labs
Questions can be assessed automatically based on the configuration of the system or application. The specification for automated assessment is shown below:
```
assessment:
    - question: "Harden your server"
      type: auto
      name: "Linux Hardening"
      script: linux_harden_assessment.py
      script_language: python
      server: cyberarena-linux-hardening
      operating_system: linux
 ```
In the example above, the linux_harden_assessment.py script will be downloaded onto the server cyberarena-linux-hardening and run once per minute. If the configuration is correct, the script will mark the question as complete and answered. A diagram of the components involved in the assessment is shown below. 

![Automated Assessment in the Google Cloud](https://user-images.githubusercontent.com/50633591/216970454-e28d927c-5873-4e5a-b7c2-9064edb2af0f.png)

An example script for assessment is shown here:
```
#!/usr/bin/python3
import os
import requests

class Assessment:
    # Include the question number from the build specification. Also, include other variables here for the script.
    QUESTION_NUMBER = "0"


def assess():
    # Program whatever configuration assessment needs to run. Return True if successful. Otherwise, return False.
    # This will run once per minute on the target machine.


def mark_complete():
    url = os.environ.get('URL')
    q_key = os.environ.get(f'Q{Assessment.QUESTION_NUMBER}_KEY')
    build_id = os.environ.get('BUILD_ID')

    data = {
        "question_id": q_key,
    }

    requests.put(f"{url}{build_id}", json=data)


if assess():
    mark_complete()
    print("Workout Complete")
else:
    print("Incomplete")

```
