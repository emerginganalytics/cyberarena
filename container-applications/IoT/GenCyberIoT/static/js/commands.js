function override(command, device_id, dest_url) {
    /*
    *  Handles data sent from override command input.
    *  Not currently supported. Expected IOT workout ~2.0
    */
}

function send_command(command, device_id, dest_url, tab_idx, reload=true) {
    /*
    *  ABOUT: Used to send basic commands to IOT device
    *  PARAMS:
    *         command => type: string, value: this.button.value
    *         device_id => type: string, value: Registered device ID
    *         dest_url => type: string, value: URL to send POST request to
    *  RETURNS:
    *         If POST request is successful, it waits 5s before making a GET
    *         request and reloading the page with new content.
    */
    let quick_commands = {'command': command,
                            'device_id': device_id};
    console.log()
    $.ajax(dest_url,{
        method: 'POST',
        data: JSON.stringify(quick_commands),
        dataType: "json",
        contentType: "application/json",
        success : function(data) {
            console.log('AJAX Success!');
            if (reload){
                reloadContent();
            }
        },
        error : function(e){
            console.log('AJAX ERROR!');
            console.log(e);
            let error_div = $('#command-result-error' + tab_idx);
            error_div.html('');
            let error_string = 'Jinkies! Something doesn\'t look right. Error message: ' + e;
            error_div.html(error_string);
        }
    });
    async function reloadContent(){
        /*
        * This function waits 12s before making a get request
        * and reloading the page.
        */
        var url = window.location.href;
        var xmlHttp = new XMLHttpRequest();
        await sleep(5000);
        xmlHttp.open("GET", url,true);
        xmlHttp.send(null);

        // reload the page with
        window.location = url;
    }
}
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

    document.getElementById(tabName).style.display = "block";
    evt.currentTarget.className += " active";
}


