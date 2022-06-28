//Teacher Home Page
function change_student_auth(newValue){
    /*  Used to change the authentication for new classes between email and anonymous
        Email requires students to authenticate with either a gmail account or username/password
        Anonymous allows any user with a landing page link to access a workout
        This can only be set upon class creation
    */
    if(newValue === 'email'){
      document.getElementById('class_student_count_div').style.display = "none";
      document.getElementById('num_students_input').value = 0;

    } else{
      document.getElementById('class_student_count_div').style.display = "block";
    }
}
function show_student_name_form(student_name, class_id){
    
    var new_name = prompt("Enter a new name for student " + student_name);
    if(new_name){
        $.ajax({
            type: "POST",
            url: "/teacher/api/change_roster_name/" + class_id + "/" + student_name,
            data: JSON.stringify({
                "new_name": new_name
            }),
            success: function(){
                let roster_element = document.getElementById('class_' + class_id + "_roster");
                let student_element = roster_element.querySelectorAll(`ul > div > #student_${student_name}`);
                let change_name_link = student_element[0].querySelectorAll('a');
                let updated_link = change_name_link[0].outerHTML.replace(student_name, new_name);
                student_element[0].innerHTML = new_name +" " + updated_link;
            }
        })
    }
}

function remove_student(class_id){
    //Removes a student name from a class
    //IMPORTANT: removes based on name, avoid students with duplicate names
    var student_name = prompt("Enter the name of the student to remove: ");
    if(student_name){
        $.ajax({
            type: "POST",
            url: "/teacher/api/change_class_roster/" + class_id,
            data: JSON.stringify({
                "action": "remove",
                "student_name":student_name
            }),
            success: function(){
                window.location.reload();
            }
        })
    }
}

function add_new_student(class_id, student_auth){
    //Used to add a single student to a class, provided the student name and the generated datastore ID of the class entity
    //If the class requires registration, a student email must also be provided
    var new_student_name = prompt("Enter the new student's name");
    data = {
        "action": "add",
        "student_name": new_student_name
    }
    if(student_auth != 'anonymous'){
        var student_email = prompt("Enter the student's email address");
        if(student_email == "" || student_email == null){
            return;
        }
        data['student_email'] = student_email;
    }

    if(new_student_name != null && new_student_name != ""){
        $.ajax({
            type: "POST",
            url: "/teacher/api/change_class_roster/" + class_id,
            data: JSON.stringify(data),
            success: function(){
                window.location.reload();
            }
        })
    }
}

function prepare_multi_student_form(class_id){
    //Used to add multiple students at a single time
    //Useful for copy/pasting entire rosters into the class
    var class_id_input = document.getElementsByClassName('multi_student_addition_classId');
    for(var i = 0; i < class_id_input.length; i++){
        class_id_input[i].value = class_id;
    }
}

function post_multiple_students(auth_method){
    //POST request to store multiple student entities inside a class
    //If email registration is required, each student name must be accompanied by an email
    if(auth_method === 'anonymous'){
        var student_list = document.getElementById('new_anonymous_student_list');
    } else {
        var student_list =document.getElementById('new_registered_student_list');
    }
    var class_id = document.getElementsByClassName('multi_student_addition_classId')[0].value;
    $.ajax({
        type: "POST",
        url: "/teacher/api/add_multiple_students",
        data: JSON.stringify({
        class_id: class_id,
        new_student_list: student_list.value
        }),
        success: function(data){
        var response_data = $.parseJSON(data)
        if(response_data['result'] == 'success'){
            student_list.value = "";
            $('#multiple_registered_students_modal').modal('hide');
            alert("Students added to class");
            window.location.reload();
        } else{
            alert("Failed to add students:\n" + response_data['result']);
        }
        }
    })

}

function change_student_name(workout_id){
    //Changes a student's name
    var name_element = document.getElementById("name_change_field_" + workout_id);
    var new_name = name_element.value;
    if(new_name == ""){
        return false;
    }
    var data = {
        "workout_id": workout_id,
        "new_name": new_name,
    }
    $.ajax({
        type: "POST",
        url: "/teacher/api/change_student_name/" + workout_id,
        data: data,
        success: function(update){
            document.getElementById('workout_student_name_' + workout_id).innerHTML = update;
            name_element.value = "";
        }
    });
}

function unclaim_workout(workout_id){
    var name_element = document.getElementById("name_change_field_" + workout_id);
    var data = {
        "workout_id": workout_id,
    }
    $.ajax({
        type: "POST",
        url: "/teacher/api/unclaim_workout/" + workout_id,
        data: data,
        success: function(update){
            document.getElementById('workout_link_' + workout_id).innerHTML = update;
            name_element.value = "";
        }
    });
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
    // var time = date + ' ' + month + ' ' + year + ' ' + hour + ':' + min + ':' + sec ;
    // return time;
    return date + ' ' + month + ' ' + year + ' ' + hour + ':' + min + ':' + sec ;
}

//Arena functions
function update_scores(team_name, score){
    var team = team_name;
    var score = score;
    score_field = document.getElementById('team_score_' + team);
    score_field.innerHTML = score;
}

function get_teams(select){
    //Used by the team change select on the manage tab for an individual student in the arena
    //Gets the list of possible teams, and displays them as options in the select element
    var team_list = document.getElementsByClassName("team_container");
    var option_list = select.children;
    
    for(var i = 0; i < team_list.length; i++){
        if(!select.querySelector('option[value="' + team_list[i].id + '"]')){
            var option = document.createElement('option');
            option.value = team_list[i].id;
            option.innerHTML = option.value;
            option.className = option.value;
            select.options.add(option, i);
        }           
    }  
}

function add_team(unit_id){
    //Create a new team in an arena
    var team_name = prompt("Enter the name of the team");
    if(team_name){
        $.ajax({
            type: "POST",
            url: "/teacher/api/add_team/" +  unit_id,
            data: JSON.stringify({team_name: team_name}),
            success: function(data){
                location.reload();
            }
        })
    }
}

function change_team(workout_id){
    //Assigns a student to an arena team
    //Must be used before the arena begins to avoid scoring inconsistencies
    var select_element = document.getElementById('team_select_' + workout_id).value;
    $.ajax({
        type:"POST",
        url: "/teacher/api/change_team/" + workout_id,
        data: JSON.stringify({
            new_team: select_element
        }),
        success: function(data){
            location.reload();
        }
    })
}

function copy_student_links(){
    var temp_div = document.createElement("textarea");

    var links = document.getElementsByClassName('workout-link');
    
    for(var i = 0; i < links.length; i++){
        temp_div.value += links[i].href + "\n";
    }
    temp_div.id = "temp_div";
    document.getElementById('loading-msg').append(temp_div);
    temp_div.select();
    document.execCommand("copy");
    document.getElementById('loading-msg').removeChild(temp_div);
    document.getElementById('copy_link_text').style.display = "block";
}
