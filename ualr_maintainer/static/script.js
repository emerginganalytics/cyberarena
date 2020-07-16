// // init Materialize select
// $(document).ready(function(){

//     $('select').formSelect();   

// });



// process values on the client - side
$("#build-workout").click(function () {

    console.log("click");


    var user_email = $("input#email").val();
    var workout_type = $("div.workout_type").html();
    var number_team = $("select#team").val();
    var length_availability = $("select#availability").val();

    var build_data = {
        "email": user_email,
        "type": workout_type,
        "team": number_team,
        "length": length_availability,
    }

    console.log(build_data);

    $.ajax({
        type: "POST",
        contentType: "application/json;charset=utf-8",
        url: "/update",
        traditional: "true",
        data: JSON.stringify({
            "email": user_email,
            "type": workout_type,
            "team": number_team,
            "length": length_availability,
        }),
        dataType: "json",

        // success: function (result) {

        //     console.log(result)
        //     console.log(result.redirect)
            
        //     window.location.href = result.redirect

        //     //window.location.replace(result.redirect);
        //     //console.log(result);
        // }

    });

    $("#workout-form").html("Thanks, an email will be send when your workout is ready !");

});

$("#go_dos_workout").click(function() {
    window.location.href = 'https://www.google.fr';
})





$("#stop-vm").click(function () {

    var instance_name = $(this).find('a')[0].id;
    console.log(instance_name);


    $.ajax({
        type: "POST",
        contentType: "application/json;charset=utf-8",
        url: "/stopvm",
        traditional: "true",
        data: JSON.stringify({
            "instance": instance_name,
        }),
        dataType: "json",
    });

});

$("#start-vm").click(function () {

    var instance_name = $(this).find('a')[0].id;
    console.log(instance_name);


    $.ajax({
        type: "POST",
        contentType: "application/json;charset=utf-8",
        url: "/startvm",
        traditional: "true",
        data: JSON.stringify({
            "instance": instance_name,
        }),
        dataType: "json",
    });

});


function check_workout_status(unit_id){

    $.ajax({
        type: "POST",
        contentType: "application/json;charset=utf-8",
        url: "/workout_list/" + unit_id,
        traditional: "true",
        data: JSON.stringify({
            "unit_id": unit_id,
        }),
        dataType: "json",
        success: function(data){
            console.log("Testing")
        }
    });
}