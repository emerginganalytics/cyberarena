import json
from flask import request
from utilities.datastore_functions import store_student_uploads, retrieve_student_uploads
from globals import ds_client
from calendar import timegm
import time

def get_assessment_questions(workout):
    if workout:
        if 'assessment' in workout:
            try:
                question_list = []

                if 'type' in workout['assessment']:
                    assessment_type = workout['assessment']['type']
                for question in workout['assessment']['questions']:
                    question_dict = {}
                    question_dict['question'] = question['question']
                    if question['type'] == 'input':
                        question_dict['answer'] = question['answer']
                    question_dict['type'] = question['type']
                    if workout['type'] == 'arena':
                        question_dict['point_value'] = question['points']
                        question_list.append(question_dict)
                        if 'submitted_answers' in workout:
                            for question in question_list:
                                for answer_group in workout['submitted_answers']:
                                    if answer_group['answer'] == question['answer']:
                                        question_list.remove(question)
                    else:
                        question_list.append(question_dict)
                return question_list, assessment_type
            except TypeError as e:
                print("TypeError detected")
                print(type(e))
                print(e)
    else:
        return False

def process_assessment(workout, workout_id, request, assessment):
    valid_answers = []
    if workout['type'] == 'arena':
        points = 0
        response = {}
        answer_found = False
        flag_attempt = request.form.get('answer')
        question_key = request.form.get('question_content')
        point_value = int(request.form.get('point_value'))
        unit = ds_client.get(ds_client.key('cybergym-unit', workout['unit_id']))

        for i in range(len(assessment)):
            if question_key == assessment[i].get('question') and flag_attempt == assessment[i].get('answer'):
                answer_found = True
        
        # if flag_attempt in valid_answers:
        if answer_found:
            answer_time = time.gmtime(time.time())
            time_string = str(answer_time[3]) + ":" + str(answer_time[4]) + ":" + str(answer_time[5])
            team_query = ds_client.query(kind='cybergym-workout')
            team_query.add_filter('teacher_email', '=', workout['teacher_email'])
            team_query.add_filter('unit_id', '=', workout['unit_id'])
            team_members = []

            for team_member in list(team_query.fetch()):
                team_members.append(team_member)
            answer_time_dict = {
                'answer': flag_attempt,
                'timestamp': time_string
            }

            #check if the answer has already been submitted by another team member
            if 'submitted_answers' in workout:
                if flag_attempt not in workout['submitted_answers']:
                    workout['submitted_answers'].append(answer_time_dict)
                else:
                    response = {
                        'answer_correct': True,
                        'points_gained':0,
                    }
                    return json.dumps(response)

            else:
                workout['submitted_answers'] = []
                workout['submitted_answers'].append(answer_time_dict)
            points += int(point_value)
            response = {
            'answer_correct': True,
            'points_gained': points,   
            }
            #check if this is the first time this flag has been found
            if 'found_flags' in unit:
                if flag_attempt in unit['found_flags']:
                    print("flag already found")
                else:
                    unit['found_flags'].append(flag_attempt)
                    point_value += 50
                    ds_client.put(unit)
            else:
                unit['found_flags'] = []
                unit['found_flags'].append(flag_attempt)
                point_value += 50
                ds_client.put(unit)

            for member in team_members:
                if 'points' in member:
                    prev_score = member['points']
                    prev_score += point_value
                    member['points'] = prev_score
                else:
                    member['points'] = point_value
                member['submitted_answers'] = workout['submitted_answers']
                ds_client.put(member)
        else:
            if unit['found_flags']:
                if flag_attempt in unit['found_flags']:
                    response = {
                        'answer_correct': True,
                        'points_gained': 0
                    }
                    return json.dumps(response)
            else:
                response = {
                    'answer_correct': False, 
                    'points_gained': 0
                }
                return json.dumps(response)
        return json.dumps(response)
    else: 
        num_correct = 0
        for i in range(len(assessment)):
            if(assessment[i].get('type') != 'upload'):
                valid_answers.append(assessment[i].get('answer'))

        assessment_answers = request.form.getlist('answer')
        assessment_questions = request.form.getlist('question')

        assessment_upload_prompt = request.form.getlist('upload_prompt')
        assessment_uploads = request.files.getlist('file_upload')


        store_student_uploads(workout_id, assessment_uploads)

        for i in range(len(assessment_answers)):
            
            user_input = {
                "question":assessment_questions[i],
                "answer":assessment_answers[i]
            }
            user_answer = str(user_input['answer'])
            true_answer = str(assessment[i].get('answer'))

            if valid_answers[i]:
                if(user_answer.lower() == valid_answers[i].lower()):
                    num_correct += 1

        uploaded_files = []
        urls = retrieve_student_uploads(workout_id)
        for index, item in enumerate(assessment_uploads):
            user_input = {
                "question": assessment_upload_prompt[index],
                "storage_url": urls[index]
            }
            uploaded_files.append(user_input)


        percentage_correct = num_correct / len(assessment_questions) * 100
        workout['uploaded_files'] = uploaded_files
        workout['submitted_answers'] = assessment_answers
        workout['assessment_score'] = percentage_correct
        ds_client.put(workout)
        return uploaded_files, assessment_answers, percentage_correct


def get_auto_assessment(workout):    
    if workout:
        if 'assessment' in workout:
            if workout['assessment'] and 'questions' in workout:
                question_list = []
                for question in workout['assessment']['questions']:
                    if question['type'] == 'auto':
                        question_list.append(question)
            else:
                return False
            
            if not question_list:
                return False
            
            return question_list
        else:
            return False
