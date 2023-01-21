class CountdownTimer {
    constructor(build_id, url, build_type) {
        this.target_id = 'room-timer';
        this.build_id = build_id;
        this.url = String(url); //'/api/escape-room/' + this.build_id;
        this.build_type = String(build_type);
    }
    updateTime(){
        return fetch(this.url, {method: "GET"})
            .then((response) => {
                return response.json().then((data) => {
                    let return_data = {}
                    if (this.build_type === 'unit'){
                        return {
                            'start_time': data['data']['unit']['workspace_settings']['start_time'],
                            'time_limit': data['data']['unit']['workspace_settings']['time_limit'],
                        }
                    } else if (this.build_type === 'escape_room') {
                       return {
                           'start_time': data['data']['unit']['escape_room']['start_time'],
                           'time_limit': data['data']['unit']['escape_room']['time_limit']
                        }
                    }
                });
            });
    }
    getRemainder(data){
        /*
        * Expects dictionary containing UTC timestamps: { start_time, time_limit }
        * If the difference between the end date and the start date are <=0, return 0
        * Otherwise, returns difference
        */
        let now = new Date().getTime();
        let endDate = 1000 * (data['start_time'] + data['time_limit']);
        let remainder = endDate - now;
        if (remainder > 0){
            return remainder;
        } else {
            return 0;
        }
    }
}
class Timer {
    constructor(build_id) {
        this.build_id = build_id;
        this.countdown = new CountdownTimer(build_id);
        this.target_id = this.countdown.target_id;
    }
    isHours (remainingTime){
        // Returns true if the remaining time is > 1 hour
        return (new Date().getTime() - remainingTime > (60 * 60 * 1000));
    }
    start(data){
        // Runs in intervals and periodically updates with data returned from get request
        var countdown = this.countdown;
        let timer_obj = document.getElementById(this.countdown.target_id);

        // Updates the target element matching the id set in CountdownTimer.target_id
        function timer(data, timer_obj){
            var x = setInterval(function (){
                var new_ts = countdown.getRemainder(data);
                let hours = Math.floor((new_ts % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                let minutes = Math.floor((new_ts % (1000 * 60 * 60)) / (1000 * 60));
                let seconds = Math.floor((new_ts % (1000 * 60)) / (1000));
                if (new_ts <= 0) { // Time has expired, reload current page
                    clearInterval(x);
                    window.location.reload();
                }
                if (hours < 10) {
                    hours = '0' + hours;
                }
                if (minutes < 10) {
                    minutes = '0' + minutes;
                }
                if (seconds < 10) {
                    seconds = '0' + seconds;
                }
                timer_obj.innerHTML = hours + ':' + minutes + ":" + seconds;
            },1000);
        }
        // Make sure the Escape Room isn't already expired before running the timer
        if (data['expired'] === false){
            timer(data, timer_obj);
        }
    }
}
