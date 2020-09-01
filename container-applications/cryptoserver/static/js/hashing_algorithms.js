$('#button_unsalted_hash').on('click', function() {
    const plaintext_password = $('#password').val();

    $.ajax({
        type : 'POST',
        url : '/ajax_calculate_unsalted_hash',
        data : JSON.stringify(plaintext_password),
        dataType: 'json',
        contentType: 'application/json',
        success : function(data) {
            console.log('AJAX Success!');

            display_unsalted_hash(data['hashed_password'], plaintext_password);
        },
        error : function(e) {
            console.log('AJAX Error!');
            console.log(e);
        }
    });
});

function display_unsalted_hash(hashed_password, plaintext_password) {
    let results_div = $('#unsalted_hash_results');

    results_div.html('');

    let html_string = 'Plaintext: ' + plaintext_password + '<br />';
    html_string += 'Unsalted Hash: ' + hashed_password;

    results_div.html(html_string);
}


$('#button_salted_hash').on('click', function() {
    const second_plaintext = $('#salted_password').val();

    $.ajax({
        type : 'POST',
        url : '/ajax_calculate_salted_hash',
        data : JSON.stringify(second_plaintext),
        dataType: 'json',
        contentType: 'application/json',
        success : function(data) {
            console.log('AJAX Success!');

            display_salted_hash(data['salted_hash_password'], second_plaintext);
        },
        error : function(e) {
            console.log('AJAX Error!');
            console.log(e);
        }
    });
});

function display_salted_hash(salted_hash_password, second_plaintext) {
    let salt_results_div = $('#salted_hash_results');

    salt_results_div.html('');

    let html_salted = 'Plaintext: ' + second_plaintext + '<br />';
    html_salted += 'Salted Hash: ' + salted_hash_password;

    salt_results_div.html(html_salted);
}

$(document).ready(function(){

});