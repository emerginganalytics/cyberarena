// Global Vars
var json_headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json; charset=UTF-8'
}

// Utility Methods
class TimestampToDate {
    constructor() {
        this.target_class = 'timestampField';
    }
    convert_timestamps(){
        let timestamp_list = document.getElementsByClassName(this.target_class);
        for (let i = 0; i < timestamp_list.length; i++){
            timestamp_list[i].innerHTML = this.timeConverter(timestamp_list[i].innerHTML);
        }
    }
    timeConverter(UNIX_timestamp){
        let a = new Date(UNIX_timestamp * 1000);
        let months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
        let year = a.getFullYear();
        let month = months[a.getMonth()];
        let date = a.getDate();
        let hour = a.getHours();
        let min = a.getMinutes();
        let sec = a.getSeconds();
        return date + ' ' + month + ' ' + year + ' ' + hour + ':' + min + ':' + sec ;
    }
}

function show_current_units(modal_num){
    $('#current_unit_' + modal_num).modal();
}
function build_unit(){
    var build_unit_select = document.getElementById('build-unit-select');
    selection = build_unit_select.options[build_unit_select.selectedIndex].value;

    var build_unit_a = document.getElementById('build-unit-a');
    build_unit_a.setAttribute("href", 'build/' + selection);
    return false;
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
        // i.e Template filter buttons
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
                .then((response) => response.json())
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
        .then(response => response.json())
        .then((data) => {
            if (data['status'] === 200){
                window.location.reload();
            }
        });
}

function deleteStudent(class_id, student_name){
    $('#modal_' + class_id).modal('toggle');
    // TODO: Send delete request for specific student
}

function sleep(ms){
    return new Promise(resolve => setTimeout(resolve, ms));
}
