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

function fill_active_workout_table(data){
    let table = document.getElementById('active_workout_display');

    for(let i = 0; i < data.length; i++){
        //let new_workout = document.createElement('tr')
        var row = add_element("tr", {id: "workout_row_" + data[i]['id']});

        var workout_link = add_element('a', {href: '/admin/workout/' + data[i]['id'], innerHTML: data[i]['id']})
        row.appendChild(add_element('td', {innerHTML: workout_link.outerHTML}));
        row.appendChild(add_element('td', {innerHTML: data[i]['type']}));
        if(data[i]['user_email']){
            row.appendChild(add_element('td', {innerHTML: data[i]['user_email']}));
        } else {
            row.appendChild(add_element('td', {innerHTML: " "}));
        }
        if(data[i]['student_name']){
            row.appendChild(add_element('td', {innerHTML: data[i]['student_name']}));
        } else {
            row.appendChild(add_element('td', {innerHTML: " "}));
        }

        row.appendChild(add_element('td', {innerHTML: data[i]['unit_id']}));
        row.appendChild(add_element('td', {innerHTML: data[i]['state']}));

        if(data[i]['runtime_counter']){
            row.appendChild(add_element('td', {innerHTML: data[i]['runtime_counter'], className: 'runtime_field'}));
        } else {
            row.appendChild(add_element('td', {innerHTML: "0"}));
        }
        
        if(data[i]['estimated_cost']){
            var cost = data[i]['estimated_cost']
        } else{
            var cost = "No cost info in spec";
        }
        var cost_el = add_element('td', {innerHTML: cost})
        row.appendChild(cost_el);
        table.appendChild(row);
    }   
}

function get_active_workouts(){
    let table = document.getElementById('active_workout_display');
    //console.log(table.firstElementChild);
    if(table.firstElementChild == null){
        var loader = document.getElementById('loading-msg');
        loader.style.display = "block";
        $("#loading-msg").html('Fetching active workouts' + '</br><div class="loader"></div>');
        $.ajax({
            type: "GET",
            url: "/admin/api/active_workouts",
            dataType: "json",
            success: function(data){
                loader.style.display = "none";
                fill_active_workout_table(data);
                format_runtime();
            }
        })
    }
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