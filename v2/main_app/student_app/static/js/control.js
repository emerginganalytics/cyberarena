class Control {
    /*
    * Params:
    *   build_id: String() referencing ID of workout to send action for
    *   elem_id: String() referencing ID of target HTML element containing state
    *       UI objects
    * */
    constructor(build_id=null, elem_id=null, url=null) {
        this.build_id = build_id;
        this.elem_id = elem_id;
        this.url = url + '/' + build_id;
    }
    getState(nextState){
        let elem_id = this.elem_id;
        let stateObj = document.getElementById(elem_id);
        let url = this.url;
        function updateState(state){
            if (state === nextState || state === '72'){
                window.location.reload();
            } else {
                stateObj.classList.add('transition');
                stateObj.classList.remove('running', 'stopped', 'deleted');
            }
        }
        let x = setInterval(function (){
            fetch(url, {
                method: 'GET'
            }).then((response) =>
                response.json()
            ).then((data) => {
                let state = data['data']['state'];
                updateState(state);
            });
        }, 30000); // 5min => 300000
    }
    toggle(state){
        let startButton = document.getElementById('startWorkoutBtn');
        let stopButton = document.getElementById('stopWorkoutBtn');
        let workoutStateObj = document.getElementById('workoutStateObj');
        if (state === 50){
           workoutStateObj.innerHTML = 'ENTER WORKOUT';
           workoutStateObj.disabled = false;
           stopButton.disabled = false;
           startButton.disabled = true;
        } else if (state === 53){
           workoutStateObj.innerHTML = 'STOPPED';
           workoutStateObj.disabled = true;
           stopButton.disabled = true;
           startButton.disabled = false;
        } else {
            workoutStateObj.innerHTML = 'WAITING';
            workoutStateObj.disabled = true;
            stopButton.disabled = true;
            startButton.disabled = true;
        }
    }
    start(){
        fetch(this.url + '?action=2', {
            method: 'PUT',
        }).then((response) =>
            response.json()
        ).then((data) => {
            if (data['status'] === 200){
                this.getState(50);
            }
        });
    }
    stop(){
        fetch(this.url + '?action=4', {
            method: 'PUT'
        }).then((response) =>
            response.json()
        ).then((data) => {
            if (data['status'] === 200) {
                this.getState(53);
            }
        });
    }
}
