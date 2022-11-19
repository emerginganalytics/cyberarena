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
    $("div.table_title").html('<h4>Select an Attack Template: </h4>');
    vulnTemplateListeners();
    // Resets form if modal close or cancel buttons are clicked
    $('button.cancel-form').click(function(){
        var table = $('#vuln-templates-table');
        table.find('.selected').removeClass('selected');
        table.find('.checkmark').removeClass('checkmark');
        enable_object('vuln-template-btn', false, true);
    });
}
function vulnTemplateListeners(){
    $('#vuln-templates-table tr').click(function(){
        const table = $('#vuln-templates-table')
        if (!$(this).hasClass('selected')) {
            // First remove all previous selected elements
            table.find('.selected').removeClass('selected');
            table.find('.checkmark').removeClass('checkmark');
            // Add selected class / checkmark to current item
            $(this).addClass('selected');
            $(this).find('#attack-checkmark-span').addClass('checkmark');
            enable_object('vuln-template-btn', true);
        } else {
            $(this).removeClass('selected');
            table.find('.checkmark').removeClass('checkmark');
            enable_object('vuln-template-btn', false, true);
        }
    });

    // Vuln form listeners
    $('#vuln-template-btn').click(function(){
        console.log('requesting template ...');
        let build_id = $('#vuln-templates-table tr.selected').attr('id');
        $.ajax({
            type: 'GET',
            contentType: 'application/json;charset=utf-8',
            traditional: true,
            url: '/api/agency/templates/' + build_id,
            processData: false,
            dataType: "json",
            success: function (data){
                console.log(data['data']);
                build_form(data['data']);
            },
            error: function(jqXHR, textStatus, errorThrown){
                console.log(textStatus);
                console.log(errorThrown);
            }
       });
    });

    $('#attack-template-form').submit(function(e){
        e.preventDefault();
        e.stopPropagation();
        $('#attack-form-modal').modal('hide');
        // Grab form data
        let form_data = {}
        let serialized = $('#attack-template-form').serialize().split("&");
        for (var key in serialized){
            let fieldValue = serialized[key].split("=")[1];
            form_data[serialized[key].split("=")[0]] = decodeURI(fieldValue);
        }
        form_data = JSON.stringify(form_data);
        console.log(form_data);
        $.ajax({
            type: "POST",
            contentType: "application/json",
            data: form_data,
            url: '/api/agency/',
            processData: false,
            dataType: "json",
            success: function(data){
                console.log(data);
            },
            error: function(jqXhR, textStatus, errorThrown){
                console.log(textStatus);
                console.log(errorThrown);
            }
        });
    });
}
function build_form(data){
    /*
    * Builds form with data received from vuln-template-table POST request
      let vulnForm = $('#attack-template-form');
    */
    let vulnFormDiv = $('#attack-form-variables');
    // First clean up any old form values
    document.getElementById('attack-form-variables').innerHTML = '';
    // Set Modal title
    document.getElementById('attack-modal-title').innerText = 'Build ' + data['name'] + ' Attack';

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
   vulnFormDiv.append(aid_div);

   // Create field for attack_mode
    let amode_div = document.createElement('div')
    amode_div.className = 'form-group';
    // Attack Mode Input
    let amode_input = document.createElement('input');
    amode_input.type = 'text';
    amode_input.name = 'mode';
    amode_input.value = data.mode;
    amode_input.readOnly = true;
    amode_input.hidden = true;
    amode_input.className = 'readOnly';
    // Add fields to form
    amode_div.appendChild(amode_input);
    vulnFormDiv.append(amode_div);

    // Create arg label and select field
   for (let arg = 0; arg < data.args.length; arg++){
       if (data.args[arg].id !== 'target_network'){
           // Create wrapper div
           let arg_div = document.createElement('div');
           arg_div.className = 'form-group';
           // Create arg select field
           let arg_select = document.createElement("select");
           if ('Choices' in data.args[arg]) {
               arg_select.name = 'attack_option';
           } else {
               arg_select.name = data.args[arg].id;
           }
           arg_select.id = data.args[arg].id;
           // Create arg label
           var arg_label = document.createElement('label');
           arg_label.htmlFor = data.args[arg].id;
           arg_label.textContent = data.args[arg].name + ': ';
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
               vulnFormDiv.append(arg_div);
           }
       }  // end !target_network
   } // end args for loop
   // Form is built; Toggle form modal
    $('#attack-form-modal').modal();
}
