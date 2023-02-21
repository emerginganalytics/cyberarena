// Global Vars
var json_headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json; charset=UTF-8'
}

// Utility Methods
function show_modal_card(modal_id){
    $('#' + modal_id).modal('toggle');
}

function enable_object(obj_id, enable, hide=false, clear=false) {
    let obj = $('#' + obj_id);
    if (typeof enable == "boolean") {
        obj.attr('hidden', hide);
        console.log('disabled = ' + enable);
        if (enable === true) {
            obj.prop('disabled', false);
            obj.prop('aria-disabled', false);
            obj.removeClass('disabled');
        } else {
            obj.addClass('disabled');
            obj.prop('disabled', true);
            obj.prop('aria-disabled', true);
        }
        // Cases where we want to remove old form artifacts,
        // i.e. Template filter buttons
        if (clear === true) {
            obj.innerHTML = "";
        }
    }
}

function select_all(caller, class_name){
    // Takes in caller obj and class name to search for and selects all checkboxes
    // containing the input class name.
    let checkboxes = document.getElementsByClassName('' + class_name);
    for (let i=0, n=checkboxes.length; i < n; i++){
        if (checkboxes[i].parentElement.id === caller.id){
            checkboxes[i].checked = caller.checked;
        }
    }
    toggleTableControl('table-action');
}

function toggleTableControl(){
    // Enables the server control buttons based on class, server-action
    let target_buttons = document.getElementsByClassName('table-action');
    $('.classIdRow').on('change', function (){
        let checked_classes = document.querySelectorAll('input[name="class_id"]:checked');
        console.log(checked_classes.length);
        for (let i=0, n=target_buttons.length; i < n; i++){
            if (target_buttons[i].id === 'deleteClassBtn') {
                let btnParent = target_buttons[i].parentElement;
                let msg = '';
                if (checked_classes.length > 1) {
                    msg = 'Cannot delete multiple!';
                } else if (checked_classes.length === 0) {
                    msg = 'Must select a Class!';
                }
                btnParent.setAttribute('title', msg);
                btnParent.setAttribute('data-original-title', msg);
                btnParent.setAttribute('tooltip', 'update');
                btnParent.setAttribute('tooltip', 'show');
                continue;
            }
            enable_object(target_buttons[i].id, this.checked);
        } // end for
    });
    $('.select-all').on('change', function (){
        // Add event listener for select-all checkbox
        for (let i=0, n=target_buttons.length; i < n; i++){
            if (target_buttons[i].id === 'deleteClassBtn') {
                let msg = '';
                msg = 'Cannot delete multiple!';
                let btnParent = target_buttons[i].parentElement;
                btnParent.setAttribute('title', msg);
                btnParent.setAttribute('data-original-title', msg);
                btnParent.setAttribute('tooltip', 'update');
                btnParent.setAttribute('tooltip', 'show');
                continue;
            }
            enable_object(target_buttons[i].id, this.checked);
        } // end for
    });
}

function change_student_auth(newValue){
    /*  Used to change the authentication for new classes between email and anonymous
        Email requires students to authenticate with either a gmail account or username/password
        Anonymous allows any user with a landing page link to access a workout
        This can only be set upon class creation
    */
    const studentCountInput = document.getElementById('student-count');
    const studentCountDiv = document.getElementById('student-count-div');
    if(newValue === 'email'){
        studentCountInput.value = '';
        studentCountInput.hidden = true;
        studentCountDiv.style.display = "none";

    } else{
        studentCountInput.hidden = false;
        studentCountDiv.style.display = "block";
    }
}

function createNewClass(){
    const createClassForm = document.querySelector('#create-class-form');
    if (createClassForm) {
        const submitCreateClass = document.getElementById('submitCreateClass');
        submitCreateClass.addEventListener("click", function (e) {
            e.stopImmediatePropagation();
            e.preventDefault();
            submitCreateClass.disabled = true;
            $("#create-class-modal").modal('hide');

            // Convert form to json object
            const formData = {};
            for (const pair of new FormData(createClassForm)) {
                formData[pair[0]] = pair[1];
            }
            console.log(formData);

            // Send POST request
            fetch('/api/classroom/', {
                method: 'POST',
                headers: json_headers,
                body: JSON.stringify(formData),
            })
                .then((response) => {
                    if (response.status === 200){
                        return response.json()
                    }
                })
                .then((data) => {
                    if (data['status'] === 200) {
                        sleep(30).then( () => {window.location.reload()});
                    } else {
                        const errorP = document.getElementById('error-msg-p');
                        errorP.textContent = data['status'] + ': ' + data['message'];
                    }
                });
        });
    }
}

function confirmDeleteClass(){
    let checked_classes = document.querySelectorAll('input[name="class_id"]:checked');
    if (checked_classes.length === 1){
        let class_id = checked_classes[0].id;
        $('#modal_' + class_id).modal('toggle');
    }
}

function deleteClass(class_id){
    $("#modal_" + class_id).modal('toggle');
    fetch('/api/classroom/' + class_id, {
        method: 'DELETE',
        headers: json_headers
    })
        .then(response => {
            if (response.status === 200){
                return response.json()
            }
        })
        .then((data) => {
            if (data['status'] === 200){
                window.location.reload();
            }
        });
}

function deleteStudent(class_id, student_name){
    $('#modal_' + class_id).modal('toggle');
    //TODO: Send delete request for specific student
}

function sleep(ms){
    return new Promise(resolve => setTimeout(resolve, ms));
}

function checkState(build_id, url){
    let new_url = url + build_id + '?state=true';
    updateStates();
    function updateStates(){
        let state_classes = ['running', 'stopped', 'deleted', 'transition'];
        fetch(new_url, {
            method: 'GET',
        }).then(response => {
            if (response.status === 200){
                return response.json()
            }
        }).then((data) =>{
            if (data['status'] === 200) {
                let states = data['data']['states'];
                if (data['data']['exists'] === true){
                    for (let i = 0; i < states.length; i++) {
                        let icon = document.getElementById('workoutState-' + String(states[i]['id']));
                        if (icon){
                            icon.classList.remove(...state_classes);
                            if (states[i]['state'] in state_classes) {
                                icon.classList.add(states[i]['state']);
                            } else if (states[i]['state'] === 'ready') {
                                icon.classList.add('stopped');
                            } else {
                                icon.classList.add('transition');
                            }
                        } else { // A workout is built that doesn't exist on current page; Reload
                            window.location.reload();
                        }
                    }
                }
            }
        });
    }
    // Initial States loaded; Start polling every 5 minutes
    setInterval(function (){
        updateStates();
    }, 70000);
}
function displayWaitingMessage(modal_id){

    // first hide form modal
    show_modal_card(modal_id);
    // display waiting message modal
    show_modal_card('waiting-message-modal');
}
function markComplete(question_id, build_id, url){
    let json_data = JSON.stringify({'question_id': question_id, 'build_id': build_id});
    fetch(url, {
        method: 'PUT',
        headers: json_headers,
        body: json_data
    }).then(response => {
        if (response.status === 200){
            return response.json()
        }
    }).then((data) =>{
        if (data['status'] === 200){
            let complete = document.get(question_id + '-complete');
            complete.innerHTML = 'TRUE';
            complete.classList.remove('incomplete');
            complete.classList.add('complete');
        }
    });
}
function startEscapeRoomTimer(build_id, url, action) {
    let URL = url + build_id;
    let json_data = JSON.stringify({'unit_action': action, 'build_id': build_id})
    fetch(URL, {
        method: 'PUT',
        headers: json_headers,
        body: json_data
    }).then(response => {
        if (response.status === 200){
            return response.json()
        }
    }).then((data) =>{
        console.log(data);
    })
}
function validateDateTime(element){
    // Compares selected datetime-local object and if the obj is <= now + 2 hours, set
    // value to min value
    let selectedDate = new Date(element.value).getTime();
    let min = new Date(new Date().getTime() + 2 * 60 * 60 * 1000);
    if (selectedDate < min.getTime()){
        let year = min.getFullYear();
        let month = formatDate(min.getMonth() + 1);
        let day = formatDate(min.getDate());
        let hours = formatDate(min.getHours());
        let minutes = formatDate(min.getMinutes());
        let formattedDateTime = year + '-' + month + '-' + day + 'T' + hours + ':' + minutes;
        console.log(formattedDateTime);
        element.value = formattedDateTime;
    }
    function formatDate(dt_obj){
        if (dt_obj < 10){
            return '0' + dt_obj;
        }
        return dt_obj;
    }
}

function filter_build_specs(filter_id) {
    var input, filter, filter_group, filter_type, cards, cardContainer;
    input = document.getElementById('buildWorkoutFilter');
    filter_group = document.getElementById('filter_group').value;
    //filter_type = document.getElementById('filter_type').value;
    filter_type = 'cardTitle';

    // Get all cards by group
    cardContainer = document.getElementById(filter_group);
    cards = cardContainer.getElementsByClassName('card');

    // Filter Items based on select type
    filter = input.value.toUpperCase();
    if (filter_type === 'cardTitle'){
        filter_titles(filter, cards);
    } else if(filter_type === 'cardTag'){
        filter_tags(filter, cards);
    }

    function filter_titles(filter, cards){
        var title, h5, i;
        for (i = 0; i < cards.length; i++){
            title = cards[i].querySelector(".card-body h5.card-title");
            if (title.innerText.toUpperCase().indexOf(filter) > -1){
                cards[i].style.display = "";
            } else {
                cards[i].style.display = "none";
            }
        }
    }
    function filter_tags(filter, cards){
        var tags, h5, i;
        for(i = 0; i < cards.length; i++){
            tags = cards[i].querySelector(".card-body div.filterTags");
            if (tags.innerText.toUpperCase().indexOf(filter) > -1) {
                cards[i].style.display = "";
            } else {
                cards[i].style.display = 'none';
            }
        }
    }
}
function hide_spec_groups(){
    var filter_group = document.getElementById('filter_group').value;
    console.log(filter_group);
    let group_ids = ['buildAssignmentRow', 'buildLiveRow', 'buildEscapeRoomRow'];
    // Hide all remaining groups
    group_ids.forEach(group => document.getElementById(group).style.display = 'none');
    // Display selected group
    document.getElementById(filter_group).style.display = 'block';
}