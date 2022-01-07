import json
from flask import request
from utilities.globals import ds_client, log_client, LOG_LEVELS, workout_globals
import time


class CyberArenaAssessment:
    """
    Created: 2021-07-11
    By: Philip Huff

    Eventually, we can make all functions in this file class-based, but I'm starting with a few minor functions
    to improve the dynamic answer capabilities for assessments.
    """
    class BUILD_TYPES:
        ARENA = "arena"
        COMPUTE = "compute"

    def __init__(self, workout_id):
        self.workout_id = workout_id
        self.workout = ds_client.get(ds_client.key('cybergym-workout', self.workout_id))
        self.assessment_info = self.workout['assessment'] if 'assessment' in self.workout else None
        self.submitted_answers = self.workout['submitted_answers'] if 'submitted_answers' in self.workout else None
        self.uploaded_files = self.workout['uploaded_files'] if 'uploaded_files' in self.workout else []
        """
            Get workout build type to determine how to process assessment submissions
                - Arena submissions add points to all workouts assigned to the same team
                - Regular workouts simply store the submitted answer / files in the datastore
        """
        unit = ds_client.get(ds_client.key('cybergym-unit', self.workout['unit_id']))
        self.workout_build_type = unit['build_type']
        
    def create_dynamic_answer(self, workout, question_number, answer):
        """
        Create a dynamic answer. Typically called when the workout starts up and creates an arbitrary flag or answer
        for the assessment.
        TODO: This functions has not been used or tested.
        @param workout: DataStore Entity holding the workout.
        @type workout: Dict
        @param question_number: The number to change
        @type question_number: Int
        @param answer: The answer to the assessment question
        @type answer: String
        @return: Status
        @rtype: Boolean
        """
        workout_question = workout['assessment']['questions'][question_number]
        is_dynamic = workout_question.get('dynamic', False)
        if is_dynamic:
            workout_question = workout['assessment']['questions'][question_number]
            has_changed = workout_question.get('has_changed', False)
            if not has_changed:
                workout_question['answer'] = answer
                workout_question['has_changed'] = True
                ds_client.put(workout)
                return True
        return False

    def get_assessment_questions(self):
        question_list = []
        for question in self.assessment_info['questions']:
            question_dict = {}
            question_dict['question'] = question['question']
            if question['type'] == 'input':
                question_dict['answer'] = question['answer']
            question_dict['type'] = question['type']
            if question['type'] == 'auto':
                question_dict['key'] = question['key'] if 'key' in question else None
                question_dict['complete'] = question['complete']

            if self.workout_build_type == self.BUILD_TYPES.ARENA:
                question_dict['point_value'] = question['points']
                question_list.append(question_dict)
                if self.submitted_answers:
                    for question in question_list:
                        for answer_group in self.submitted_answers:
                            if answer_group['answer'] == question['answer']:
                                question_list.remove(question)
            else:
                question_list.append(question_dict)
        return question_list

    def submit(self):
        """
            Handles submission for an individual question from a workout. Calls the appropriate function depending on workout type
            @param submission: Dict containing question text and the user submitted answer. 
        """
        if self.workout_build_type == self.BUILD_TYPES.ARENA:
            submission = {
                "answer": request.form['answer'],
                "question": request.form['question']
            }
            result = self._submit_flag(submission)
        else:
            student_upload = request.files.getlist('file_upload')
            if student_upload:
                upload_index = request.form.getlist('upload_index')
                prompt = request.form.getlist('upload_prompt')
                result = self._upload_file(student_upload, prompt, upload_index)
            else:
                submission = {
                    "answer": request.form['answer'],
                    "question": request.form['question']
                }
                result = self._store_answer(submission)
        return result

    @staticmethod
    def get_startup_scripts(workout_id, assessment):
        """
        Parses the assessment specification to obtain any startup script metadata on the specified server.
        Returns the startup script data for common.build_workout to include in the specified server startup script
        metadata.
        :param workout_id: The ID of the workout assessment being parsed
        :param assessment: A dictionary structured according to the assessment specification in the yaml where
        each question may have an auto assessment script which needs to run.
        :return: An array of dictionaries specifying the server and startup script or none if there are no startup
        scripts. The structure of a startup script
        {
            'servername': {'key': 'windows-startup-script-bat', 'value': <the specified startup script>,
        }
        """
        startup_scripts = {}
        i = 0

        for question in assessment['questions']:
            if question['type'] == 'auto':
                if question['operating-system'] == 'windows':
                    if question['server'] not in startup_scripts:
                        script = workout_globals.windows_startup_script_env.format(env_workoutid=workout_id)
                        startup_scripts[question['server']] = {
                            'key': 'windows-startup-script-bat',
                            'value': script
                        }
                    if 'script-language' in question and question['script-language'] == 'python':
                        script_command = 'python {script}'.format(script=question['script'])
                    elif 'script-language' in question and question['script-language'] == 'powershell':
                        script_command = 'powershell.exe -File ./{script}'.format(script=question['script'])
                        script_command = f'"{script_command}"'
                    else:
                        script_command = question['script']
                    assess_script = workout_globals.windows_startup_script_task.format(env_workoutkey=question['key'],
                                                                                       q_number=i,
                                                                                       script_name='Assess' + str(i),
                                                                                       script=question['script'],
                                                                                       script_command=script_command)

                else:
                    if question['server'] not in startup_scripts:
                        script = workout_globals.linux_startup_script_env.format(env_workoutid=workout_id)
                        startup_scripts[question['server']] = {
                            'key': 'startup-script',
                            'value': script
                        }
                    if 'script-language' in question and question['script-language'] == 'python':
                        script_command = f"python3 /usr/bin/{question['script']}"
                    else:
                        script_command = f"/usr/bin/{question['script']}"
                    assess_script = workout_globals.linux_startup_script_task.format(env_workoutkey=question['key'],
                                                                                     q_number=i,
                                                                                     script=question['script'],
                                                                                     local_storage="/usr/bin",
                                                                                     script_command=script_command)
                if i != 0:
                    startup_scripts[question['server']]['value'] += "\n"
                startup_scripts[question['server']]['value'] += assess_script
                i += 1

        if len(startup_scripts) == 0:
            startup_scripts = None
        return startup_scripts

    def _submit_flag(self, submission):
        """
        Handles flag submission for Arena CTF challenges. Calculates score based on value provided in the Arena yaml, with a bonus awarded
        to the first team to submit. Also marks completion for all team members.
        @param: submission: Dict generated from form submission
        """
        points = 0
        response = {}
        answer_found = False
        flag_attempt = submission['answer']
        question_key = submission['question']
        point_value = 0
        unit = ds_client.get(ds_client.key('cybergym-unit', self.workout['unit_id']))

        for i in range(len(self.assessment_info['questions'])):
            if question_key == self.assessment_info['questions'][i].get('question') and flag_attempt == self.assessment_info['questions'][i].get('answer'):
                point_value = self.assessment_info['questions'][i].get('points')
                answer_found = True
        
        # if flag_attempt in valid_answers:
        if answer_found:
            answer_time = time.gmtime(time.time())
            time_string = str(answer_time[3]) + ":" + str(answer_time[4]) + ":" + str(answer_time[5])
            team_members = []
            if 'team' in self.workout:
                team_query = ds_client.query(kind='cybergym-workout')
                team_query.add_filter('team', '=', self.workout['team'])
                team_query.add_filter('unit_id', '=', self.workout['unit_id'])
                for team_member in list(team_query.fetch()):
                    team_members.append(team_member)

            answer_time_dict = {
                'answer': flag_attempt,
                'timestamp': time_string
            }

            #check if this is the first time this flag has been found
            if 'found_flags' in unit:
                if flag_attempt not in unit['found_flags']:
                    unit['found_flags'].append(flag_attempt)
                    point_value += 50
                    ds_client.put(unit)
                    answer_time_dict['first'] = True
            else:
                unit['found_flags'] = []
                unit['found_flags'].append(flag_attempt)
                point_value += 50
                answer_time_dict['first'] = True
                ds_client.put(unit)

            #check if the answer has already been submitted by another team member
            if self.submitted_answers:
                if flag_attempt not in self.workout['submitted_answers']:
                   self.submitted_answers.append(answer_time_dict)
                else:
                    response = {
                        'answer_correct': True,
                        'points_gained':0,
                    }
                    return response

            else:
                self.submitted_answers = []
                self.submitted_answers.append(answer_time_dict)
            self.workout['submitted_answers'] = self.submitted_answers

            points += int(point_value)
            response = {
                'answer_correct': True,
                'points_gained': points,   
            }
            
            #Add submitted answer to team member entities
            if 'team' in self.workout:
                for member in team_members:
                    if 'points' in member:
                        prev_score = member['points']
                        prev_score += point_value
                        member['points'] = prev_score
                    else:
                        member['points'] = point_value
                    member['submitted_answers'] = self.submitted_answers
                    ds_client.put(member)
            else:
                if 'points' in self.workout:
                    prev_score = self.workout['points']
                    prev_score += point_value
                    self.workout['points'] = prev_score
                else:
                    self.workout['points'] = point_value
                ds_client.put(self.workout)
        else:
            response = {
                'answer_correct': False, 
                'points_gained': 0
            }
        
        return response

    def _store_answer(self, submission):
        """
            Used to store answer attempt for regular input assessment questions. 
            @param: submission: Dict generated from form submission on workout landing page
            TODO: update answer grading
        """
        answer = submission['answer']
        question = submission['question']
        new_attempt = {"question": question, "answer": answer}
        previous_attempt = False

        if not self.submitted_answers:
            self.submitted_answers = []
        for attempt in self.submitted_answers:
            if attempt['question'] == question:
                attempt['answer'] = answer
                previous_attempt = True
        if not previous_attempt:
            self.submitted_answers.append(new_attempt)
        
        self.workout['submitted_answers'] = self.submitted_answers
        
        ds_client.put(self.workout)
        return new_attempt

    def _upload_file(self, file, prompt, index):
        """
            Handles storage of image files for workout assessment questions involving screenshots. 
            Stores images in GCP Storage Bucket {project}_assessment_upload/{workout_id}
            @param file: Blob object for the image file
            @param prompt: Used to designate the question to which the image pertains
            @param index: The index of the question in the assessment object. Used to provide a unique name to the image upload in GCP
        """
        from utilities.datastore_functions import store_student_upload
        upload_url = store_student_upload(self.workout_id, file[0], index)

        if upload_url:
            for prev_upload in self.uploaded_files:
                if prev_upload['question'] == prompt:
                    prev_upload['storage_url'] = upload_url
                    self.workout['uploaded_files'] = self.uploaded_files
                    ds_client.put(self.workout)
                    return upload_url
            user_input = {
                "question": prompt,
                "storage_url": upload_url
            }
            self.uploaded_files.append(user_input)
            self.workout['uploaded_files'] = self.uploaded_files
        ds_client.put(self.workout)
        return json.dumps(user_input)

    def _get_answers(self):
        valid_answers = []
        for i in range(len(self.assessment)):
            if(self.assessment[i].get('type') != 'upload'):
                valid_answers.append(self.assessment[i].get('answer'))
        return valid_answers
        
def get_auto_assessment(workout):    
    if workout:
        if 'assessment' in workout:
            if workout['assessment'] and 'questions' in workout['assessment']:
                question_list = []
                for question in workout['assessment']['questions']:
                    if question['type'] == 'auto':
                        question_list.append(question)
                return question_list
    return False
