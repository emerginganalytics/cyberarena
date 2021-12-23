var threshold = "";
$(document).ready(function(){
    var speed = 0;

    $('#gas_control').on('click', function(){
        if(speed < 100 && (speed + 10 <= 100)){
            speed += 10;
            threshold = update_speed(speed, threshold);
        }
    })

    $('#brake_control').on('click', function(){
        if(speed > 0 && (speed - 10 >= 0)){
            speed -= 10;
            threshold = update_speed(speed, threshold);
        }
    })
    document.getElementById("command-home-tab").click();
})

function update_speed(speed, speed_interval){
    //Rotates the needle on the speedometer to specified value
    //Blue: 0-50
    //Yellow: 51-85
    //Red: 86-100
    var speed_indicator = document.getElementById('indicator');
    var speed_display = document.getElementById('speed-display');
    let currSpeed = parseInt(speed_display.innerHTML);
    var testInterval = setInterval(function(){
        speed_interval = threshold;
        
        if(speed > currSpeed){
            currSpeed += 1;
            speed_display.innerHTML = currSpeed + 'mph';
        } else {
            currSpeed -= 1;
            speed_display.innerHTML = currSpeed + 'mph';
        }
        if(currSpeed == speed){
            clearInterval(testInterval);
            threshold = update_rpi_speed(currSpeed);
        }
        
        speed_indicator.style.transform = "rotate(-" + ((currSpeed * 180) / 100) + "deg)"; 
    }, 100); 

    return threshold;
    
}

function update_rpi_speed(speed){
    var device_id = document.getElementById('device_id').innerHTML;
    if(speed < 51 && threshold != 'BLUE'){
        threshold = 'BLUE';
    }
    else if(speed > 50 && speed < 86 && threshold != 'YELLOW'){
        threshold = 'YELLOW';
    }
    else if (speed > 85 && speed <= 100 && threshold != 'RED'){
        threshold = 'RED';
    } else {
        if (speed > 100){
            threshold = 'CRITICAL';
            send_command(threshold, device_id, '/iot/commands/' + device_id + '/submit');
            return threshold;
        } else {
            return threshold;
        }
    }
    
    console.log(device_id);
    let quick_commands = {'command': threshold,
                            'device_id': device_id};
    console.log(quick_commands);
    $.ajax({
        method: 'POST',
        data: JSON.stringify(quick_commands),
        dataType: "json",
        contentType: "application/json",
        url: device_id + '/submit',
        success : function(data) {
            console.log('AJAX Success!');
            return threshold;
         },
        error : function(e){
            console.log('AJAX ERROR!');
            console.log(e);
            let error_div = $('#command-result-error');
            error_div.html('');
            let error_string = 'Jinkies! Something doesn\'t look right. Error message: ' + e;
            error_div.html(error_string);
        }
    });
    return threshold;
}
