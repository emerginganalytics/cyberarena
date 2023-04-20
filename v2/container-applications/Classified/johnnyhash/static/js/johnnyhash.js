var json_headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json; charset=UTF-8'
}
function toggle_modal(modal_id){
    $('#' + modal_id).modal('toggle');
}
function add_field(form_id) {
    // Takes form_id and div_id and appends new text field to form div
    let btn, input, count, form, inner_div, span, outer_div, span_id;
    form = document.getElementById(form_id);

    // Get current count of inputs for generating input names
    count = form.getElementsByTagName('input').length;

    // Create Input div group
    outer_div = document.createElement('div');
    outer_div.classList.add('input-group', 'input-group-sm', 'mb-3');
    inner_div = document.createElement('div');
    inner_div.classList.add('input-group-prepend');

    // Generate Span
    span = document.createElement('span');
    span.classList.add('input-group-text');
    span_id = 'inputGroup' + Number(count);
    span.id = span_id
    span.innerText = 'Password';
    inner_div.appendChild(span);
    outer_div.appendChild(inner_div);

    // Create Input field
    input = document.createElement('input');
    input.name = 'hash' + count;
    input.classList.add('form-control');
    input.type = 'text';
    input.setAttribute('aria-label', 'Password');
    input.setAttribute('aria-describedby', span_id);
    input.required = true;
    outer_div.appendChild(input);
    document.getElementById('additional-fields').appendChild(outer_div);
} // End add_field function
function reset_form(form_id){
    let addFields;
    addFields = document.getElementById('additional-fields');
    addFields.innerHTML = '';
    $('#' + form_id)[0].reset();
}

function get_hashes(form_id, url, modal_id){
    toggle_modal(modal_id);
    let form, form_data, i, j, hashTable, hashCell, valueCell, row, hash_list;
    form = document.getElementById(form_id);
    if (form) {
        form_data = form.getElementsByTagName("input");
        // Pack input values into json processable object
        hash_list = [];
        for (j=0; j < form_data.length; j++){
            hash_list.push(String(form_data[j].value));
        }
        // Clear form of currently submitted values
        reset_form(form_id);
        // POST data and load results into hash-results-table
        fetch(url, {
            headers: json_headers,
            method: 'POST',
            body: JSON.stringify({'passwords': hash_list})
        }).then(response =>
            response.json()).then((resp_data) => {
                if (resp_data['status'] === 200){
                    hashTable = document.getElementById('hash-results-table');
                    let data = resp_data['data'];
                    if (element_exists('nullRow')){
                        document.getElementById('nullRow').remove();
                    }
                    for (i = 0; i < data.length; i++){
                        // Create new row
                        row = hashTable.insertRow(-1);
                        // Create cells for hash and hash value
                        hashCell = row.insertCell(0);
                        valueCell = row.insertCell(1);
                        // Set cell values;
                        if ('error' in data[i]){
                            hashCell.innerText = data[i]['error'];
                        } else {
                            hashCell.innerText = data[i]['hash'];
                            hashCell.classList.add('hash');
                        }
                        valueCell.innerText = data[i]['password'];
                        valueCell.classList.add('hash-value');
                    } // End for loop~
                } else {
                    console.log(resp_data['status']);
                    console.log(resp_data['data']);
                }
            }
        );
    }
} // End get_hashes function

function login(form_id, url){
    toggle_modal('login-modal');
    let form, form_data, error_div;
    form = document.getElementById(form_id);
    form_data = new FormData(form);
    error_div = document.getElementById('login-error');
    for (var [key, val] of form_data.entries()){
        if (val === '' || val === null) {
            error_div.innerText = '*Missing required field: ' + key.toUpperCase();
            return;
        }
    }
    fetch(url, {
        method: 'POST',
        body: form_data,
        redirect: 'follow'
    }).then(response => {
        const contentType = response.headers.get("content-type");
        if (contentType && contentType.indexOf('application/json') !== -1) {
            return response.json().then((resp_data) => {
                if (resp_data['status'] !== 200){
                    error_div.innerText = resp_data['error_msg'];
                }
            })
        } else {
            if (response.redirected) {
                window.location.href = response.url;
            }
        }
    });
}
function element_exists(elem_id){
     var element = document.getElementById(elem_id);
    // If it isn't "undefined" and it isn't "null", then it exists.
    return typeof (element) != 'undefined' && element != null;
}

function calculateCaesar(form_id, url){
    let form, i, formData, results, resultDiv;
    form = document.getElementById(form_id);
    formData = new FormData(form);
    fetch(url, {
        method: 'POST',
        body: formData,
    }).then(response => response.json()).then((json_data)=>{
        resultDiv = document.getElementById('decryptedResults');
        if (json_data['status'] === 200){
            resultDiv.innerText = json_data['data']['plaintext'];
        } else {
            resultDiv.innerText = 'ERROR: ' + String(json_data['message']);
        }
    })
}
function checkCaesarCipher(form_id, url, idx){
    let form, formData, inputDiv;
    var object, jsonData;
    object = {};
    formData = new FormData(document.getElementById(form_id));
    formData.forEach((value, key) => object[key] = value);
    jsonData = JSON.stringify(object);
    fetch(url, {
        method: 'PUT',
        body: jsonData,
        headers: json_headers
    }).then(response => response.json()).then((json_data)=>{
        inputDiv = document.getElementById('caesarCipher' + idx);
        if (json_data['status'] === 200){
            if (json_data['data']['complete'] === true){
                inputDiv.style.backgroundColor = 'var(--mint)';
            } else {
                inputDiv.style.backgroundColor = 'var(--quaternary)';
                inputDiv.style.color = 'black';
                inputDiv.innerText = json_data['data']['message'];
            }
        } else {
            inputDiv.style.background = 'var(--quaternary)';
        }
        inputDiv.style.color = 'black';
    });
}
// [ eof]