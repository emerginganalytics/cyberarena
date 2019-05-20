let text_input = $('#text_input');
let select_input = $('#select_input');
let button_submit = $('#button_submit');

function update_submit_button() {
    if (text_input.val() != '' && select_input.val() != -1) {
        // The button can be enabled because the user has entered text and
        // made a choice in the select box
        if (button_submit.attr('disabled')) {
            button_submit.removeAttr('disabled');
            console.log('Submit Button Enabled');
        }
    }
    else {
        // The button should be disabled because either the text_input is blank
        // or the user hasn't chosen a valid choice from select_input
        button_submit.attr('disabled', 'true');
        console.log('Submit Button Disabled');
    }
}

text_input.change(function() {
    console.log('Text Input Updated');
    update_submit_button();
});

select_input.change(function() {
    console.log('Select Input Updated');
    update_submit_button();
});

$(document).ready(function() {
    console.log('Document Ready Function Fired');

    update_submit_button();
});