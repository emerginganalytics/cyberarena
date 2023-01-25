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
        this.url = url + build_id;
    }
    getState(nextState){
        let elem_id = this.elem_id;
        let stateObj = document.getElementById(elem_id);
        let url = this.url;
        function updateState(state){
            console.log('Current State::' + state);
            if (state === nextState || state === '72'){
                window.location.reload();
            } else {
                stateObj.classList.add('transition');
                stateObj.classList.remove('running', 'stopped', 'deleted');
            }
        }
        setInterval(function (){
            fetch(url, {
                method: 'GET'
            }).then((response) =>
                response.json()
            ).then((data) => {
                let state = data['data']['state'];
                updateState(state);
            });
        }, 15000); // 5min => 300000
    }
    toggle(state){
        let startButton = document.getElementById('startWorkoutBtn');
        let stopButton = document.getElementById('stopWorkoutBtn');
        let workoutStateObj = document.getElementById('workoutStateObj');
        let workoutStateIcon = document.getElementById('workoutState');
        let connectionBtns = document.getElementsByClassName('connection-link');

        if (state === 50){
           workoutStateObj.innerHTML = 'RUNNING';
           workoutStateIcon.classList.remove('transition');
           workoutStateIcon.classList.add('running');
           this.disableElement(workoutStateObj, false);
           this.disableElement(stopButton, false);
           this.disableElement(startButton);
           // this.disableElements(connectionBtns, false);
        } else if (state === 53){
           workoutStateObj.innerHTML = 'STOPPED';
           workoutStateIcon.classList.remove('transition');
           workoutStateIcon.classList.add('stopped');
           this.disableElement(workoutStateObj);
           this.disableElement(stopButton);
           this.disableElement(startButton, false);
           // this.disableElements(connectionBtns);
        } else {
            workoutStateObj.innerHTML = 'WORKING';
            workoutStateIcon.classList.remove('stopped', 'running');
            workoutStateIcon.classList.add('transition');
            this.disableElement(workoutStateObj);
            this.disableElement(stopButton);
            // this.disableElements(connectionBtns);
        }
    }
    disableElement(elem, disable=true){
        if (disable) {
            elem.classList.add('disabled', 'no-select');
            elem.disabled = true;
        } else {
            elem.classList.remove('disabled', 'no-select');
            elem.disabled = false;
        }
    }
    disableElements(elems, disable=true){
        if (disable){
            for (let btn in elems){
               this.disableElement(btn);
           }
        } else {
            for (let btn in elems){
               this.disableElement(btn, false);
           }
        }
    }
    start(){
        fetch(this.url + '?action=2', {
            method: 'PUT',
        }).then((response) =>
            response.json()
        ).then((data) => {
            if (data['status'] === 200){
                let current_state = data['data']['status'];
                this.toggle(current_state);
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
                let current_state = data['data']['status'];
                this.toggle(current_state);
                this.getState(53);
            }
        });
    }
}
