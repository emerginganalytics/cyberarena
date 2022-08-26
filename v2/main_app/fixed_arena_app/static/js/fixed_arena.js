$(document).ready(function() {
    createStocManager();
    createClassManager();
});

function send_request(args){
    /*
    * This function is adding unneeded complexity. Each object action function should have
    * their own fetch request attached. This will help with readability and reduce the amount
    * of logic needed to write at the cost of adding a few extra lines :)
    * */
    // Build the URL
    let url = '';
    if (!('url' in args)) {
        url = '/api/fixed-arena/' + args['build_type'] + '/';
        if ('build_id' in args) {
            url = '/api/fixed-arena/' + args['build_type'] + '/' + args['build_id'];
        }
    }
    else { url = args['url']; }
    let request_headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json; charset=UTF-8'
    }
    if ('data' in args) {
        if (args['method'] === 'POST'){
           fetch(url, {
                method: args['method'],
                headers: request_headers,
                body: JSON.stringify(args['data'])
            })
            .then((request) =>
                request.json())
            .then((response) => {
                success(response, true);})
            .catch((err) => {
                error(err);
            });
        }
        else {
            fetch(url, {
                method: args['method'],
                headers: request_headers,
                body: JSON.stringify(args['data'])
            })
            .then((request) =>
                request.json())
            .then((response) => {
                success(response);
            })
            .catch((err) => {
                error(err);
            });
        }
    }
    // Not sure where this is used
    else {
        fetch(url, {
            method: args['method'],
            headers: request_headers
        })
            .then((request) =>
                request.json())
            .then((response) => {
                success(response);})
            .catch((err) => {
                error(err);
            });
    }
    // Response functions
    function success(resp, clear=null) {
        if (resp['status'] === 200){
            if (clear)
                // Clear post submission history
                window.history.replaceState("", "", window.location.href)
            // Request successful, refresh location and clear any query strings, if any
            window.location.replace(window.location.href.split('?')[0]);
        }
        else {
            let errorDiv = $('error-msg-div');
            errorDiv.addClass(["text-center", "p-3", "col-10"]);

            // Create error element
            let errorP = document.createElement("p");
            errorP.id = 'error-msg-p';
            errorP.textContent = resp['message'];
            errorP.className = "text-danger";
            errorDiv.append(errorP);
        }
    }
    function error (err) {
        // Will only be called for HTTP 500
        console.log(err);
    }
}
function enable_object(obj_id, enable=false, clear=false) {
    let obj = $('#' + obj_id);
    if (typeof enable == "boolean") {
        obj.prop("disabled", enable);
        obj.prop('hidden', enable)

        // Cases where we want to remove old form artifacts,
        // i.e Template filter buttons
        if (clear === true) {
            obj.innerHTML = "";
        }
    }
}
function select_all(caller, class_name){
    // Takes in caller obj and class name to search for.
    let checkboxes = document.getElementsByClassName('' + class_name);
    for (let i=0, n=checkboxes.length; i < n; i++){
        checkboxes[i].checked = caller.checked;
    }
}
function manage_stoc(action){
    let selected = []
    $('.stocIdRow:checked').each(function () {
        selected.push(this.id);
    })

    let method = '';
    if (action === 3) {
        method = 'DELETE';
        if (selected.length > 1){
            let url = '/api/fixed-arena/?stoc_ids=' + JSON.stringify(selected)
            send_request({'url': url, 'action': action, 'method': method});
        }
        else {
            let url = '/api/fixed-arena/' + selected[0];
            send_request({'url': url, 'action': action, 'method': method});
        }
    }
    else if (action === 2 || action === 4) {
        method = 'PUT';
        send_request({'url': '/api/fixed-arena/', 'action': action, 'method': method, 'data': selected});
    }
}
function createStocManager(){
    const createStocForm = document.querySelector('#create-stoc-form');
    if (createStocForm) {
        createStocForm.addEventListener("submit", function (e) {
            e.preventDefault();
            const submitCreateStoc = document.getElementById('submitCreateStoc');
            submitCreateStoc.disabled = true;
            let stocModal = $("create-stoc-modal");
            stocModal.modal('toggle');
            stocModal.modal('hide');

            /* Convert form to json object */
            const formData = {};
            for (const pair of new FormData(createStocForm)) {
                formData[pair[0]] = pair[1]
            }
            console.log(formData);
            send_request({'url': '/api/fixed-arena/', 'method': 'POST', 'data': formData});
        });
    }
}
function manage_class(action, build_id=null) {
    let args = {}
    console.log(build_id)
    console.log(action)
    if (action === 2 || action === 4) {
        let body_data = {'action': action}
        args = {'build_type': 'class', 'build_id': build_id, 'method': 'PUT', 'data': body_data}
        send_request(args);
    }
    else if (action === 3) {
        // Hide modal and send Delete request
        let deleteModal = $("modal_" + build_id);
        deleteModal.modal('toggle');
        deleteModal.modal('hide');
        args = {'build_type': 'class', 'build_id': build_id, 'method': 'DELETE'};
        send_request(args);
    }
}
function createClassManager(){
    let args = {}
    const createClassForm = document.querySelector('#create-class-form');
    if (createClassForm) {
        createClassForm.addEventListener("submit", function (e) {
            e.preventDefault();
            const submitCreateClass = document.getElementById('submitCreateClass');
            submitCreateClass.disabled = true;
            let classModal = $('create-class-modal');
            classModal.modal('toggle');
            classModal.modal('hide');

            /* Convert form to json object */
            const formData = {};
            for (const pair of new FormData(createClassForm)) {
                formData[pair[0]] = pair[1]
            }
            args = {'build_type': 'class', 'method': 'POST', 'data': formData}
            send_request(args)
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