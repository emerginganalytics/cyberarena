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

$(document).ready(function() {

});