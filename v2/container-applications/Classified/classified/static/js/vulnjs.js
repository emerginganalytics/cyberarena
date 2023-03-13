function login(url){
    let uname = document.getElementById("uname").value;
    let passw = document.getElementById("passw").value;

    let dat = {'username':uname, 'password':passw};

    $.ajax(url,{
        method: 'POST',
        data: JSON.stringify(dat),
        dataType: "json",
        contentType: "application/json",
    }).done(function(res){

      if (res['status'] == 'success'){
        $("#stat").html('<b>Login Successful </b>' + res.flag);
      }
      else{
        $("#stat").html('<b>Login Failed</b>');
      }

    }).fail(function(err){
        $("#stat").html(err);
    });
}

$(document).ready(function(){

    $("#navbar ul li a").on('click', function(event){
        event.preventDefault();
        let page = $(this).attr("href");

        $("#main").load(page);
    });
});
