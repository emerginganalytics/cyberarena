function manage_class(action, build_id=null) {
    if (action === 3) {
        url = '/api/fixed-arena/class/' + build_id;
        var request = fetch(url, {
            method: 'DELETE',
        }).then(response => response.json()).then(response => console.log(response));
    }
    else if (action === 2 || action === 4) {
        url = '/api/fixed-arena/class/' + build_id;
        var request = fetch(url, {
            method: 'PUT',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({'action': action})
        }).then(request => request.json()).then(request => console.log(request));
    }
}
function enable_object(obj_id, enable=false, clear=false) {
    var obj = $('#' + obj_id);
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
$(document).ready(function() {
    const createClassForm = document.querySelector('#create-class-form');
    if (createClassForm) {
        createClassForm.addEventListener("submit", function(e){
            const submitCreateClass = document.getElementById('submitCreateClass');
            submitCreateClass.disabled = true;

            /* Convert form to json object */
            const formData = {};
            for (const pair of new FormData(createClassForm)){
                formData[pair[0]] = pair[1]
            }
            /* Send POST request */
            let url = '/api/fixed-arena/class/'
            const response = fetch(url, {
                method: "POST",
                headers: {
                'Content-type': 'application/json; charset=UTF-8'
                 },
                body: JSON.stringify(formData)
            }).then(response => response.json()).then(response => console.log(response));
        });
    }
});
$(document).ready(function() {
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
        var form_data = {}
        for (var key in serialized){
            form_data[serialized[key].split("=")[0]] = serialized[key].split("=")[1];
        }
        // TODO: GET UNIT_ID for current fixed arena
        form_data['unit_id'] = 'temp_unit_id';
        console.log(form_data);
        $('#vuln-form-modal').modal('hide');
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
    });
});
// Builds form with data received from vuln-template-table POST request
function build_form(data){
    var vulnForm = $('#vuln-template-args');
    // First clean up any old form values
   document.getElementById('vuln-template-args').innerHTML = '';

   // Create field for attack_id
   var aid_div = document.createElement('div');
   aid_div.className = 'form-group';
   // Attack ID Input
   var aid_input = document.createElement('input');
   aid_input.type = 'text';
   aid_input.name = 'attack_id';
   aid_input.value = data.id;
   aid_input.readOnly = true;
   aid_input.className = 'readOnly';
   // Attack ID label
   var aid_label = document.createElement('label');
   aid_label.htmlFor = 'attack_id';
   aid_label.innerText = 'Attack ID: ';
   // Add fields to form
   aid_div.appendChild(aid_label);
   aid_div.appendChild(aid_input);
   vulnForm.append(aid_div);

    // Create arg label and select field
   for (var arg = 0; arg < data.args.length; arg++){
       if (data.args[arg].id !== 'target_network'){
           // Create wrapper div
           var arg_div = document.createElement('div');
           arg_div.className = 'form-group';
           // Create arg select field
           var arg_select = document.createElement("select");
           arg_select.name = data.args[arg].id;
           arg_select.id = data.args[arg].id;
           // Create arg label
           var arg_label = document.createElement('label');
           arg_label.htmlFor = data.args[arg].id;
           arg_label.textContent = data.args[arg].name + ':';
           if ('Choices' in data.args[arg]){
               for (var i = 0; i < data.args[arg].Choices.length; i++){
                    var option_i = document.createElement('option');
                    var option_key = Object.keys(data.args[arg]['Choices'][i])[0];
                    option_i.name = option_key;
                    option_i.value = option_key.toString();
                    option_i.textContent = option_key;

                    // check for default value
                    var current_choice = data['args'][arg]['Choices'][i];
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
