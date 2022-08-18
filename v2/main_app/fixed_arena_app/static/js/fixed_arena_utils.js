$(document).ready(function() {
    createStocManager();
    createClassManager();
    vulnTemplateManager();
});

function send_request(args){
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
function vulnTemplateManager(){
       // TODO: Remove display number rows option; Set default value to 10 with overflow being sent to
       //       new page
    $('#vuln-templates-table').DataTable({
        "paging": false,
        "bInfo": false,
        "columns": [
            {searchable: true, orderable: true},
            {searchable: true, orderable: false},
            {searchable: true, orderable: true},
            {searchable: false, orderable: false},
        ],
        "dom": '<"table_title">frtip',
    });
    $("div.table_title").html('<h3>Select an Attack Template: </h3>');

    // Resets form if modal close or cancel buttons are clicked
    $('button.cancel-form').click(function(){
        var table = $('#vuln-templates-table');
        table.find('.selected').removeClass('selected');
        table.find('.checkmark').removeClass('checkmark');
        enable_object('vuln-template-btn');
    });

    // Vuln form listener
    $('#vuln-template-form').submit(function(e){
        e.preventDefault();
        let post_url = $(this).attr('action');
        let request_method = $(this).attr("method");
        let serialized = $(this).serialize().split("&");

        // build json object from serialized form
        let form_data = {}
        for (var key in serialized){
            form_data[serialized[key].split("=")[0]] = serialized[key].split("=")[1];
        }
        form_data['stoc_id'] = 'temp_stoc_id';
        console.log(form_data);
        $('#vuln-form-modal').modal('hide');

        let args = {'url': post_url, 'method': request_method, 'data': form_data}
        send_request(args);
        /*
        $.ajax({
            type: request_method,
            contentType: 'application/json;charset=utf-8',
            traditional: true,
            url: post_url,
            data: JSON.stringify(form_data),
            processData: false,
            dataType: "json",
            success: function (data){
                console.log(data);
            },
            error: function(jqXHR, textStatus, errorThrown){
                console.log(textStatus);
                console.log(errorThrown);
            }
       });
       */
    });
}
function build_form(data){
    // Builds form with data received from vuln-template-table POST request
    let vulnForm = $('#vuln-template-args');
    // First clean up any old form values
   document.getElementById('vuln-template-args').innerHTML = '';

   // Create field for attack_id
   let aid_div = document.createElement('div');
   aid_div.className = 'form-group';
   // Attack ID Input
   let aid_input = document.createElement('input');
   aid_input.type = 'text';
   aid_input.name = 'attack_id';
   aid_input.value = data.id;
   aid_input.readOnly = true;
   aid_input.className = 'readOnly';
   // Attack ID label
   let aid_label = document.createElement('label');
   aid_label.htmlFor = 'attack_id';
   aid_label.innerText = 'Attack ID: ';
   // Add fields to form
   aid_div.appendChild(aid_label);
   aid_div.appendChild(aid_input);
   vulnForm.append(aid_div);

    // Create arg label and select field
   for (let arg = 0; arg < data.args.length; arg++){
       if (data.args[arg].id !== 'target_network'){
           // Create wrapper div
           let arg_div = document.createElement('div');
           arg_div.className = 'form-group';
           // Create arg select field
           let arg_select = document.createElement("select");
           arg_select.name = data.args[arg].id;
           arg_select.id = data.args[arg].id;
           // Create arg label
           var arg_label = document.createElement('label');
           arg_label.htmlFor = data.args[arg].id;
           arg_label.textContent = data.args[arg].name + ':';
           if ('Choices' in data.args[arg]){
               for (let i = 0; i < data.args[arg].Choices.length; i++){
                    let option_i = document.createElement('option');
                    let option_key = Object.keys(data.args[arg]['Choices'][i])[0];
                    option_i.name = option_key;
                    option_i.value = option_key.toString();
                    option_i.textContent = option_key;

                    // check for default value
                    let current_choice = data['args'][arg]['Choices'][i];
                    if (current_choice === data.args[arg].default){
                        option_i.defaultSelected = true;
                    }
                    arg_select.appendChild(option_i);
               } // end Choices for loop
               // Append generated fields to form
               arg_div.appendChild(arg_label);
               arg_div.appendChild(arg_select);
               vulnForm.append(arg_div);
           }
       }  // end !target_network
   } // end args for loop
   // Form is built; Toggle form modal
    $('#vuln-form-modal').modal();
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