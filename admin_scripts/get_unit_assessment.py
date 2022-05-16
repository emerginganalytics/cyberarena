from common.globals import ds_client, BUILD_STATES

def get_unit_assessment(unit_id):
    workout_list = ds_client.query(kind="cybergym-workout")
    workout_list.add_filter('unit_id', '=', unit_id)

    for workout in list(workout_list.fetch()):
        if 'student_name' in workout and workout['student_name']:
            output_str = ""
            question_list = ""

            if 'submitted_answers' in workout:
                questionNum = 0
                num_submitted = 0
                for question in workout['assessment']['questions']:
                    questionNum += 1
                    if question['type'] == 'auto':
                        if question['complete'] == True:
                            num_submitted += 1
                            question_list += f"\n\t{questionNum}: Complete"
                        else:
                            question_list += f"\n\t{questionNum}: Not Completed"
                    for answer in workout['submitted_answers']:
                        if answer['question'] == question['question']:
                            if answer['answer']:
                                num_submitted += 1
                                question_list += f"\n\t{questionNum}: Submitted {answer['answer']}\tTrue Answer: {question['answer']}"
                                if answer['answer'].lower() == question['answer'].lower():
                                    question_list += "\t\tGraded: Correct"
                                else:
                                    question_list += "\t\tGraded: Incorrect"
                            else:
                                question_list += f"\n\t{questionNum}: Not Submitted"
                                
                output_str += f"=====\n{workout['student_name']} Submitted: {num_submitted}/{len(workout['assessment']['questions'])}"
            if output_str:
                print(output_str)
            if question_list:
                print(question_list)
