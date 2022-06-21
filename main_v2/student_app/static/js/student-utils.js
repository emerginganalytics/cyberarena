function server_action(action, server_name){
    $.ajax({
        type: "POST",
        url: "/student/server_management/{{ workout.key.name }}",
        contentType: "application/json",
        data: JSON.stringify({
            "action": action,
            "server_name": server_name
        })
    })
}
function prepare_survey(){
    //Set up display modal for student feedback survey
    var modal = document.getElementById("surveyModal");
    var btn = document.getElementById("surveyBtn");
    var span = document.getElementsByClassName("close-modal")[0];

    btn.onclick = function() {
        modal.style.display = "block";
    }

    span.onclick = function() {
        modal.style.display = "none";
    }

    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = "none";
        }
    }

    $("#survey_form").on('submit',function(event){
        event.preventDefault();
        var feedback_data = new FormData(this);
        $.ajax({
                type: "POST",
                url: "/student/feedback/{{ workout.key.name }}",
                data: feedback_data,
                contentType: "application/json;charset=utf-8",
                data: feedback_data,
                contentType: false,
                processData: false,
                success: function(data){
                    var jsonData = JSON.parse(data);
                    alert("Survey submitted!");
                }
            })
    });
}
function prepare_assessment(){
    $(".workout_assessment_form").submit(function(e) {
        e.preventDefault();
        $("#loading-msg").html('Please wait while the process completes' +
            '</br><div class="loader"></div>');

        var form = $(this);
        var url = form.attr('action');

        //Serialize form data
        var assessment_data = new FormData(this);
        $.ajax({
            //Send data to server and add the submitted answer to the answered questions display
            type: "POST",
            url: url,
            data: assessment_data,
            contentType: false,
            processData: false,
            success: function(data)
            {
                $("#loading-msg").html("");
                var jsonData = JSON.parse(data);
                if(jsonData["answer"]){
                    //Find previous submission and update answer on page
                    var submitted_answers = document.querySelectorAll(".submitted_answer_group > .submitted_question");
                    for(var i = 0; i < submitted_answers.length; i++){
                        if(submitted_answers[i].innerHTML == "Question: " + jsonData["question"]){
                            let answer_element = submitted_answers[i].nextElementSibling;
                            answer_element.innerText = "Submission: " + jsonData['answer'];
                            return;
                        }
                    }
                    //If no previous attempt, create new submission div for this question
                    var new_submission_element = document.createElement('div');
                    new_submission_element.className = "submitted_answer_group";

                    var question_element = document.createElement('p');
                    question_element.innerHTML = "Question: " + jsonData["question"];
                    question_element.className = "submitted_question";
                    new_submission_element.appendChild(question_element);

                    var answer_element = document.createElement('p');
                    answer_element.innerHTML = "Submission: " + jsonData["answer"];
                    answer_element.className = "submitted_answer";
                    new_submission_element.appendChild(answer_element);

                    $("#submitted_answers").append(new_submission_element);
                }
            }
        });
        //Reset form and activate the submission indicator check mark
        this.reset();
        var form_question = this.querySelectorAll(".question_group > p > .submission_indicator");
        form_question.forEach(element => element.innerHTML = "&#10004");
        return false;
    });
    $("assessment_reveal").click(function(){
        $("#assessment_form").fadeIn();
    });
}
function redirect_to_landing(workout_id){
    window.location.href = "/student/landing/" + workout_id;
}
function timeConverter(UNIX_timestamp){
    var a = new Date(UNIX_timestamp * 1000);
    var months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
    var year = a.getFullYear();
    var month = months[a.getMonth()];
    var date = a.getDate();
    var hour = a.getHours();
    var min = a.getMinutes();
    var sec = a.getSeconds();
    var time = date + ' ' + month + ' ' + year + ' ' + hour + ':' + min + ':' + sec ;
    return time;
}
