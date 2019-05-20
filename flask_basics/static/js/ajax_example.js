let button_add_something = $('#button_add_something');
let text_input = $('#text_input');
let div_my_list = $('#div_my_list');
let my_stuff = [];

button_add_something.click(function() {
    console.log('Add Button Clicked');

    let user_input = text_input.val();

    $.ajax({
        type : 'POST',
        url : '/ajax_add_item',
        data : JSON.stringify(user_input),
        dataType: 'json',
        contentType: 'application/json',
        success : function(data) {
            console.log('AJAX Success!');
            my_stuff.push(data['new_item']);
            show_my_stuff();
        },
        error : function(e) {
            // Deal with errors here
            console.log('AJAX Error!');
            console.log(e);
        }
    });
});

function show_my_stuff() {
    console.log('show_my_stuff() fired');

    let html_string = '';

    for (let i = 0; i < my_stuff.length; i++) {
        html_string += my_stuff[i] + '<br />';
    }

    div_my_list.html(html_string);
}

$(document).ready(function() {
    my_stuff = [];

    show_my_stuff();
});