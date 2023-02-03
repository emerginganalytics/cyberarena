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
    toggle(state, func1=null, func2=null){
        let startButton = document.getElementById('startWorkoutBtn');
        let stopButton = document.getElementById('stopWorkoutBtn');
        let workoutStateObj = document.getElementById('workoutStateObj');
        let workoutStateIcon = document.getElementById('workoutState');
        let connectionBtns = document.getElementsByClassName('connection-link');

        // Set functions to handle disabling elements
        let disableElement = '';
        let disableElements = '';
        if ((func1 !== null) && (func2 !== null)) {
            disableElement = func1;
            disableElements = func2;
        } else {
            disableElement = this.disableElement;
            disableElements = this.disableElements;
        }

        if (state === 50){
           workoutStateObj.innerText = 'RUNNING';
           workoutStateIcon.classList.remove('transition', 'stopped');
           workoutStateIcon.classList.add('running');
           disableElement(workoutStateObj, false);
           disableElement(stopButton, false);
           disableElement(startButton);
           disableElements(connectionBtns, false, disableElement);
        } else if (state === 53){
           workoutStateObj.innerText = 'STOPPED';
           workoutStateIcon.classList.remove('transition', 'running');
           workoutStateIcon.classList.add('stopped');
           disableElement(workoutStateObj);
           disableElement(stopButton);
           disableElement(startButton, false);
           disableElements(connectionBtns, true, disableElement);
        } else {
            workoutStateObj.innerText = 'WORKING';
            workoutStateIcon.classList.remove('stopped', 'running');
            workoutStateIcon.classList.add('transition');
            disableElement(workoutStateObj);
            disableElement(stopButton);
            disableElement(startButton);
            disableElements(connectionBtns, true, disableElement);
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
    disableElements(elems, disable=true, disableElement){
        if (disable){
            for (let i = 0; i < elems.length; i++){
               disableElement(elems[i]);
           }
        } else {
            for (let i = 0; i < elems.length; i++){
                disableElement(elems[i], false);
            }
        }
    }
    start(){
        this.toggle(52);
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
        this.toggle(51)
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
    poll(){
        // A passive state checker that polls workout state every 5 minutes
        let elem_id = this.elem_id;
        let stateObj = document.getElementById(elem_id);
        let url = this.url + '?state=true';

        // We need to declare which functions we want to use otherwise, JS is unable to find the
        // appropriate function attached to <this>
        let toggle = this.toggle;
        let func1 = this.disableElement;
        let func2 = this.disableElements;

        // Start the poll
        setInterval(function (){
            fetch(url, {
                method: 'GET'
            }).then((response) =>
                response.json()
            ).then((data) => {
                let state = data['data']['state'];
                toggle(state, func1, func2);
            });
        }, 300000);
    }
}
