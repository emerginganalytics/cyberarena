/**
 * File: session-manager.js
 *
 * Author: Johnny Hash
 *
 * For: Web Interface for IoT Stationary Health (WIISH)
 *
 * About:
 *  Management said that I needed to make the website more secure, so I created this class to
 *  help authenticate the user.
 *
 *  Now even if users modify the HTML they should not be able to access our *CRITICAL* *PATIENT* data!
 *  Sessions are authenticated with a predefined UID and an access token.
 *  Guest users (uid=2) are given this *token* by default: 3tR2aJ8BQgf99TRkE7xxHMQ4Q2lW5qFX
 *
 *  I know this isn't the most secure method, but surely it's good enough until I can get some rest, right?
 *
 *  Usage:
 *      var sm = new SessionManager(cyber-arena-***);
 *
 *      // Get session user id:
 *      uid = sm.getSessionCookie('uid');
 *
 *      // Set session user id:
 *      sm.setSessionCookie('uid', 2);
 *
 *      // Get authentication token associated with cached uid
 *      token = sm.getToken();
 *      ...
 * */
class SessionManager {
    constructor(device_id=String, url=null) {
        this.device_id = device_id;
        this.url = url;
    }

    send_command(command, dest_url, reload=true){
        /*
        * ABOUT: Used to send basic commands to IoT device
        * PARAMS:
        *       command => type: string, value: this.button.value
        *       device_id => type: string, value: Registered device_id (cyber-arena-***)
        *       dest_url => type: string, value: URL to send POST request to
        *       reload => type: bool, value: Whether to reload page after successful requests
        * RETURNS:
        *       if POST succeeds, it waits 5s before making a GET request and reloading
        *       the page with the new content.
        *
        * TODO: This method isn't working quite right and I'm too tired to figure this out right now.
        *  Maybe I'm missing something in the object that I am sending ...
        * */
        let quick_commands = {'command': command, 'device_id': this.device_id}
        $.ajax(dest_url, {
            method: 'POST',
            data: JSON.stringify(quick_commands),
            dataType: "json",
            contentType: "application/json",
            success: function (data){
                console.log('Command Sent!');
                if (reload === true){
                    var resp = reloadContent();
                    console.log(resp);
                }
            },
            error: function (e){
                console.log(e);
                let error_div = $('#command-result-error');
                error_div.html('');
                let error_str = 'Jinkies! Something doesn\'t look right. Error: ' + e;
                error_div.html(error_str);
            }
        })
        async function reloadContent(){
            /*
            * This function waits 5s before making a get request
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
    };

    setSessionCookie(name, value){
        /*
        * Used to set session cookie values. These values should be persistent until
        * the browser is closed.
        * */
        document.cookie = name + '=' + value + ';';
    }
    getSessionCookie(name){
        /*
        * Takes cookie name, decodes the document cookie string before splitting the string
        * into an array at each instance of a semicolon.
        * It then loops through the generated array for the cookie matching the input name.
        * If a match is found, return it otherwise return an empty string.
        * */
        let cname = name + '=';
        let decoded = decodeURI(document.cookie);
        let ca = decoded.split(';');
        for (let i = 0; i < ca.length; i++){
            let c = ca[i];
            while (c.charAt(0) == ' '){
                c = c.substring(1);
            }
            if (c.indexOf(cname) == 0){
                return c.substring(cname.length, c.length);
            }
        }
        return "";
    }
    getToken(){
        /*
        * Tokens are required with each POST request so that the server knows to trust
        * the incoming command.
        * Tokens change based on which level of access the current user has,
        * */
        let uid = this.getSessionCookie('uid');
        if (uid){
            let url = window.location.href + "/token?uid=" + uid;
            this._getToken(uid, url);
        } else {
            console.log('Could not find session cookie, uid. Did you set it?');
        }
    }
    _getToken(uid, url){
        // Sends GET request to server to fetch authentication token associated with session cookie, uid
        fetch(url)
            .then((response) => response.json())
            .then((json) => console.log(json));
    }
}