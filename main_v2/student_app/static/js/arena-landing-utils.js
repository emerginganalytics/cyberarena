function reveal_assessment(){
    $(".workout_assessment_form").fadeToggle();
}
function check_workout_state(){
    var state = $.ajax({
        type:"POST",
        url: "/workout_state/{{ workout.key.name }}",
        traditional: "true",
    });
    return state;
}

function update_state(){
    var state_display = document.getElementById("workout_state_display");
    var workout_link = document.getElementById("workout_link");
    check_workout_state().then( new_state => {
        if(new_state == "RUNNING"){
            workout_link.style.visibility = "visible";
            state_display.style.color = "green";
            state_display.innerHTML = "RUNNING";
            $(".loader").remove();
        } else if(new_state == "READY"){
            workout_link.style.visibility = "hidden";
            state_display.style.color = "red";
            state_display.innerHTML = "STOPPED";
            $(".loader").remove();
        } else{
            workout_link.style.visibility = "hidden";
            state_display.style.color = "orange";
            state_display.innerHTML = "WORKING";
            $(".loader").remove();
        }
    });
}
$(document).ready(function(){
    update_state();
    var state_checker = setInterval(update_state, 15000);
    $(".flag_form").submit(function(e) {
        e.preventDefault();
        $("#loading-msg").html('Please wait while the process completes' +
            '</br><div class="loader"></div>');
        var form = $(this);
        var url = form.attr('action');
        $.ajax({
            type: "POST",
            url: url,
            data: form.serialize(), // serializes the form's elements.
            dataType: "json",
            success: function(data)
            {
                $("#loading-msg").html("");
                if(data['answer_correct']){
                    alert("Correct answer");
                    form.parent().fadeOut();
                }else{
                    alert("Incorrect Flag");
                }
            }
            });
    });
});