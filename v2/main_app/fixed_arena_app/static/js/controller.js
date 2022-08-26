/*
* @author Andrew Bomberger
* @copyright Copyright 2022, UA Little Rock, Emerging Analytics Center
* @license MIT
* @since 1.0.0
* */
$(document).ready(function (){
    vulnTemplateManager();
})

function vulnTemplateManager(){
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
    /*
    * Builds form with data received from vuln-template-table POST request
    */
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
