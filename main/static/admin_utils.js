function format_runtime(){
    //Formats runtime counter into hours/minutes instead of seconds
    var runtime_list = document.getElementsByClassName('runtime_field');
    for(var i = 0; i < runtime_list.length; i++){
        var runtime_s = runtime_list[i].innerHTML;
        var hours = Math.floor((runtime_s / 3600))
        var minutes = Math.floor((runtime_s % 3600) / 60)
        var formatted_runtime = hours.toString() + " hours " + minutes.toString() + " minutes";
        runtime_list[i].innerHTML = formatted_runtime;
    }
}

function toggle_new_spec_form(){
    //Displays the form for new workout spec creation
    var spec_form = document.getElementById('new_workout_spec_form');
    if (spec_form.style.display === 'none'){
        spec_form.style.display = "block";
    } else {
        spec_form.style.display = "none";
    }
}

function admin_action(action, user_email){
    //POST to app for admin-only functions
    //Possible actions include approving/denying users, promoting other users to admin, running cloud scripts, etc
    $.ajax({
        type: "POST",
        url: "/admin/home",
        data: JSON.stringify({
            "action": action,
            "user_email": user_email
        }),
        success: function(data){
            var json = $.parseJSON(data);
            if(json['action_completed']){
                location.reload();
            }else{
                alert("Action denied");
            }
        }
    })
}

function workout_search(){
    //Used by the search bar on the Maintenance tab
    //Filters based on the value of the select field next to the search bar
    var search_filter= document.getElementById('filter_select').value;
    var search_term = document.getElementById('search_term').value;
    var table = document.getElementById('active_workout_table');
    var rows = table.getElementsByTagName('tr');
    for(var i = 0; i < rows.length; i++){
        var row = rows[i].getElementsByTagName('td');
        if(row){
            for(var j = 0; j < row.length; j++){
                if(row[j].className == (search_filter + "_field")){
                    if(row[j].getElementsByTagName('a').length > 0){
                        if (row[j].firstChild.innerHTML.toUpperCase().trim() != search_term.toUpperCase().trim()){
                            rows[i].style.display = "none";
                        } else{
                            rows[i].style.display = "";
                        }
                    }
                    else if(row[j].innerHTML.toUpperCase().trim() != search_term.toUpperCase().trim()){
                        rows[i].style.display = "none";
                    }
                    else{
                        rows[i].style.display = "";
                    }
                }
            }
        }

    }
    document.getElementById('clear_filter_button').style.display = "";
}

function clear_filter(){
    //Removes active filters from the Maintenance table
    var table = document.getElementById('active_workout_table');
    var rows = table.getElementsByTagName('tr');
    for(var i = 0; i < rows.length; i++){
        rows[i].style.display = "";
    }
    document.getElementById('clear_filter_button').style.display = "none";
}