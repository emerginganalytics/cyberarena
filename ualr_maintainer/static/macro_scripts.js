function nuke_workout(workout_id){
    $.ajax({
        type: "POST",
        contentType: "application/json;charset=utf-8",
        url: "/nuke_workout/" + workout_id,
        traditional: "true",
        data: JSON.stringify({
            "workout_id": workout_id,
        }),
        dataType: "json",
        success: function(data){
            if(data['build_type'] == "compute" || data['build_type'] == "compute"){
                window.location.href="/landing/" + data['workout_id'];
            }else if(data['build_type'] == 'arena'){
                window.location.href="/arena_landing" + data['workout_id'];
            }
        },
    });
    $('.nuke_btn').click();
}