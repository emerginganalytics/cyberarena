$(document).ready(function() {
    createStocManager();
    createClassManager();
    toggleServerControl();
});
var json_headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json; charset=UTF-8'
}

/*
success(){
    let errorDiv = $('error-msg-div');
    errorDiv.addClass(["text-center", "p-3", "col-10"]);

    // Create error element
    let errorP = document.createElement("p");
    errorP.id = 'error-msg-p';
    errorP.textContent = resp['message'];
    errorP.className = "text-danger";
    errorDiv.append(errorP);
}
function error (err) {
    // Will only be called for HTTP 500
    console.log(err);
}
*/
function toggleServerControl(){
    // Enables the server control buttons based on class, server-action
    let target_buttons = document.getElementsByClassName('server-action');
    $('.stocIdRow').on('change', function (){
        var checked_stocs = $('input[name=stoc_id]:checked');
            for (let i=0, n=target_buttons.length; i < n; i++){
                if (target_buttons[i].id === 'deleteStocBtn') {
                    let btnParent = target_buttons[i].parentElement;
                    let msg = '';
                    if (!checked_stocs.length === 1){
                        if (checked_stocs.length > 1) {
                            msg = 'Cannot delete multiple!';
                        } else if (!checked_stocs.length) {
                            msg = 'Must select a build!';
                        }
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
            if (target_buttons[i].id === 'deleteStocBtn') {
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
        checkboxes[i].checked = caller.checked;
    }
    toggleServerControl('server-action');
}
function setDatetimeLimits(){
    let today = new Date();
    let day = today.getDay();
    let month = today.getMonth();
    let year = today.getFullYear();
    if (day < 10) {
        day = '0' + day;
    }
    if (month < 10) {
        // Max date allowed for classes is 3 months
        if (month + 3 >= 10) {
            month = month + 3;
        }
        else {
            month = '0' + month;
        }
    }
    let min_date = year + '-' + month + '-' + day;
    let max_date = year + '-' + month + '-' + day;
    document.getElementById('class-expire-date').setAttribute("min", min_date);
    document.getElementById('class-expire-date').setAttribute("max", max_date);
}
function manage_stoc(action){
    let selected = []
    $('.stocIdRow:checked').each(function () {
        selected.push(this.id);
    })
    let url = '/api/fixed-arena/';
    if (action === 3) {
        if (selected.length === 1) {
            url = url + selected[0];
            $("#modal_delete_fa").modal('toggle');
            fetch(url, {
                method: 'DELETE',
                headers: json_headers,
            })
                .then((response) => response.json())
                .then((data) => {
                    if (data['status'] === 200) {
                        new StateManager(2, selected[0], 72).getState();
                    }
                });
        } else {
            console.warn('400: BAD REQUEST!');
        }
    }
    else if (action === 2 || action === 4) {
        // START or STOP request
        let jsonData = '';
        if (selected.length === 1) {
            var build_id = selected[0];
            url = url + build_id;
            jsonData = JSON.stringify({'build_id': build_id, 'action': action});
        } else {
            jsonData = JSON.stringify({'stoc_ids': selected, 'action': action});
        }
        fetch(url, {
            method: 'PUT',
            headers: json_headers,
            body: jsonData,
        })
            .then((response) => response.json())
            .then((data) => {
                if (data['status'] === 200) {
                    let endState = ''
                    if (action === 2) {
                        endState = 50;
                    } else {
                        endState = 53;
                    }
                    new StateManager(2, build_id, endState).getState();
                }
            });
    }
}
function createStocManager(){
    const createStocForm = document.querySelector('#create-stoc-form');
    if (createStocForm) {
        createStocForm.addEventListener("submit", function (e) {
            e.stopImmediatePropagation();
            e.preventDefault();
            const submitCreateStoc = document.getElementById('submitCreateStoc');
            submitCreateStoc.disabled = true;
            $("#create-stoc-modal").modal('hide');
            /* Convert form to json object */
            const formData = {};
            for (const pair of new FormData(createStocForm)) {
                formData[pair[0]] = pair[1]
            }
            console.log(formData);
            fetch('/api/fixed-arena/', {
                method: 'POST',
                headers: json_headers,
                body: JSON.stringify(formData),
                })
                    .then((response) => response.json())
                    .then((data) => {
                        if (data['status'] === 200) {
                            new StateManager(2, formData['stoc_id'], 53).poll_create_stoc('stoc-table');
                        }
                    });
        });
    }
}
function manage_class(action, build_id=null) {
    let end_state = 0;
    if (action === 2 || action === 4) {
        let body_data = {'action': action}
        fetch('/api/fixed-arena/class/' + build_id, {
            method: 'PUT',
            headers: json_headers,
            body: JSON.stringify(body_data)
        })
            .then(response => response.json())
            .then((data) => {
                if (action === 4) {
                    end_state = 53;
                } else {
                    end_state = 50;
                }
                new StateManager(3, build_id, end_state).getState();
            });
    }
    else if (action === 3) {
        // Hide modal and send Delete request
        $("#modal_" + build_id).modal('toggle');
        fetch('/api/fixed-arena/class/' + build_id, {
            method: 'DELETE',
            headers: json_headers
        })
            .then(response => response.json())
            .then((data) => {
                new StateManager(3, build_id, 72).getState();
            });
    }
}
function createClassManager(){
    const createClassForm = document.querySelector('#create-class-form');
    if (createClassForm) {
        createClassForm.addEventListener("submit", function (e) {
            e.stopImmediatePropagation();
            e.preventDefault();
            const submitCreateClass = document.getElementById('submitCreateClass');
            submitCreateClass.disabled = true;
            // Close modal
            $('#create-class-modal').modal('hide');

            /* Convert form to json object */
            const formData = {};
            for (const pair of new FormData(createClassForm)) {
                formData[pair[0]] = pair[1]
            }
            fetch('/api/fixed-arena/class/', {
                method: 'POST',
                headers: json_headers,
                body: JSON.stringify(formData),
                })
                    .then((response) => response.json())
                    .then((data) => {
                        if (data['status'] === 200) {
                            new StateManager(3, formData['stoc_id'], 53).poll_create_class();
                        }
                    });
        });
    }
}
function copy_student_links(){
    let temp_div = document.createElement("textarea");
    let links = document.getElementsByClassName('workspace-link');
    for (var i = 0; i < links.length; i++){
        temp_div.value += links[i].href + "\n";
    }
    temp_div.id = "temp_div";
    document.getElementById('loading-msg').append(temp_div);
    temp_div.select();
    document.execCommand("copy");
    document.getElementById('loading-msg').removeChild(temp_div);

    // Display copy success message
    let copy_link_text = document.getElementById('copy_link_text')
    copy_link_text.style.display = "inline-text";
    sleep(30);
    copy_link_text.style.display = 'none';
}
function manage_student(student_num, build_id, registration_required){
    // Changes a student's name and/or email
    let name_element = document.getElementById("name_change_field_" + student_num);
    let email_element = document.getElementById("email_change_field_" + student_num)
    let new_name = name_element.value;
    let new_email = email_element.value;

    if(new_name == ""){
        return false;
    }
    let data = {
        "build_id": build_id,
        "new_name": new_name,
        "new_email": new_email
    }
    $.ajax({
        type: "PUT",
        url: "/api/fixed-arena/class/" + build_id,
        data: data,
        success: function(update){
            document.getElementById('workspace' + workout_id).innerHTML = update;
            name_element.value = "";
        }
    });
}
// [ eof ]
