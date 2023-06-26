function sendDeviceID(device_id, dest_url, caller) {
    if (device_id.trim().length === 0 ){
        let disp_msg = 'Missing Device ID!';
        display_error(disp_msg);
        return;
    }
    let msg = JSON.stringify({"device_id": device_id});
    console.log(msg);

    $.ajax(dest_url, {
        method: 'POST',
        data: msg,
        dataType: "json",
        contentType: "application/json",
        success : function(data) {
            let errorDiv = document.getElementById('error-msg-div');
            errorDiv.style.visibility = "hidden";
            console.log('AJAX Success!');
            diagonalWipe(caller);
            if (data['url']){
               this.redirectUser(data['url']);
            }
        },
        error : function(e) {
            let errorDiv = document.getElementById('error-msg-div');
            let errorMsg = document.getElementById('error-msg-p');
            var msg = JSON.parse(JSON.stringify(e));
            errorMsg.innerHTML = msg['responseJSON']['error_msg'];
            errorDiv.style.visibility = "visible";
        },
        async redirectUser(url){
             await sleep(3000);
             window.location.replace(url);
        }
    });
    function  display_error(error_msg) {
        let errorDiv = document.getElementById('error-msg-div');
        let errorMsg = document.getElementById('error-msg-p');
        errorMsg.innerText = error_msg;
        errorDiv.style.visibility = "visible";
    }
}

function sleep(ms){
    // params: ms (time in milliseconds)
    console.log("Sleeping for " + ms);
    return new Promise(resolve => setTimeout(resolve, ms));
}


function openTab(evt, tabName){
    var tabContent = document.getElementsByClassName("tabContent");
    for(var i = 0; i < tabContent.length; i++){
        tabContent[i].style.display = "none";
    }

    var tabLinks = document.getElementsByClassName("tabLinks");
    for(var i = 0; i < tabLinks.length; i++){
        tabLinks[i].className = tabLinks[i].className.replace(" active", "");
    }

    document.getElementById(tabName).style.display = "grid";
    evt.currentTarget.className += " active";
}

