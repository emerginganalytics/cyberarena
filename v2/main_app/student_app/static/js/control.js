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
        let url = this.url + '?state=true';
        function updateState(state){
            if (state === nextState || state === '72' || state === '62'){
                window.location.reload();
            } else {
                stateObj.classList.add('transition');
                stateObj.classList.remove('running', 'stopped', 'deleted', 'broken', 'notbuilt');
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
        }, 5000);
    }
    toggle(state, func1=null, func2=null, servers=true){
        // Control Elements
        var loadingIcon;
        let startWorkoutLi = document.getElementById('startWorkoutLi');
        let startButton = document.getElementById('startWorkoutBtn');
        let stopButton = document.getElementById('stopWorkoutBtn');
        let workoutStateObj = document.getElementById('workoutStateObj');
        let workoutStateIcon = document.getElementById('workoutState');
        let connectionBtns = document.getElementsByClassName('connection-link');
        let extendWorkoutLi = document.getElementById('extendWorkoutLi');
        let extendDurationBtn = document.getElementById('extendDurationBtn');
        // Timer Elements
        let roomTimerDiv = document.getElementById('room-timer-div');
        let roomTimerInput = document.getElementById('runtimeDuration');

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

        if (state === 1){
            // Disable rebuild button
            let rebuildBtn;
            rebuildBtn = document.getElementById('rebuildWorkoutBtn');
            loadingIcon = rebuildBtn.querySelector('.loading-icon');
            loadingIcon.classList.add('animated');
            disableElement(rebuildBtn, true);
            // Add working status
            workoutStateObj.innerText = 'WORKING';
            workoutStateIcon.classList.remove('stopped', 'running', 'broken', 'notbuilt');
            workoutStateIcon.classList.add('transition');
            disableElement(workoutStateObj);
            // Disable All
            if (servers){
                disableElement(stopButton);
                disableElement(startButton);
            }
        }
        else if (state === 50){
           workoutStateObj.innerText = 'RUNNING';
           workoutStateIcon.classList.remove('transition', 'stopped');
           workoutStateIcon.classList.add('running');
           // Display Timer Div
            disableElement(roomTimerDiv, false, 'block');
            disableElement(roomTimerInput, true, 'none');
           if (servers){
               // Enable Stop Btn
               disableElement(workoutStateObj, false);
               disableElement(stopButton, false);
               // Disable and Hide Start Btn
               disableElement(startButton, true, 'none');
               disableElement(startWorkoutLi, true, 'none');
               // Enable and Show Extend Duration Btn
               disableElement(extendDurationBtn, false);
               disableElements(extendWorkoutLi, false);
           }
           // Enable Connection Btns
           disableElements(connectionBtns, false, disableElement);
        }
        else if (state === 53){
           workoutStateObj.innerText = 'STOPPED';
           workoutStateIcon.classList.remove('transition', 'running');
           workoutStateIcon.classList.add('stopped');
           disableElement(workoutStateObj);
           // Display Timer Div
            disableElement(roomTimerDiv, true, 'none');
            disableElement(roomTimerInput, false);
           // Disable Stop Btn
           disableElement(stopButton);
           // Enable and show Start Btn
           disableElement(startButton, false);
           disableElement(startWorkoutLi, false);
           // Disable and Hide Extend Btn
           disableElement(extendDurationBtn, true, 'none');
           disableElement(extendWorkoutLi, true, 'none');
           // Disable Connection Btns
           disableElements(connectionBtns, true, disableElement);
        } else if (state === 72) {
            workoutStateObj.innerText = 'DELETED';
            workoutStateIcon.classList.remove('transition', 'running', 'stopped');
            workoutStateIcon.classList.add('deleted');
            disableElement(workoutStateObj);
            // Disable All
            disableElement(roomTimerDiv, true, 'none');
            disableElement(roomTimerInput, true, 'none');
            disableElement(stopButton);
            disableElement(startButton, false);
            // Hide Extend Workout Btn
            disableElement(extendDurationBtn, true, 'none');
            disableElement(extendWorkoutLi, true, 'none');
            disableElements(connectionBtns, true, disableElement);
        } else if (state === 62) {
            // Add state text
            workoutStateObj.innerText = 'BROKEN';
            workoutStateIcon.classList.remove('transition', 'running', 'stopped');
            workoutStateIcon.classList.add('broken');
            disableElement(workoutStateObj);
            // Disable All but Stop Button
            disableElement(roomTimerDiv, true, 'none');
            disableElement(roomTimerInput, true, 'none');
            disableElement(stopButton, false);
            disableElement(startButton);
            // Hide Extend Workout Btn
            disableElement(extendDurationBtn, true, 'none');
            disableElement(extendWorkoutLi, true, 'none');
            disableElements(connectionBtns, true, disableElement);
        }
        else {
            workoutStateObj.innerText = 'WORKING';
            workoutStateIcon.classList.remove('stopped', 'running', 'broken', 'notbuilt');
            workoutStateIcon.classList.add('transition');
            disableElement(workoutStateObj);
            // Timer Div
            disableElement(roomTimerDiv, true, 'block');
            disableElement(roomTimerInput, true, true);
            // Disable All
            disableElement(stopButton);
            disableElement(startButton);
            // Hide Extend Workout Btn
            disableElement(extendDurationBtn, true, 'none');
            disableElement(extendWorkoutLi, true, 'none');
            disableElements(connectionBtns, true, disableElement);
        }
    }
    disableElement(elem, disable=true, display='inline'){
        /*
        * Args:
        *   elem => Target HTML element to disable
        *   disable => Boolean value for whether to disable the object; True by default
        *   hide => Boolean value for whether to hide the object; False by default;
        * */
        if (disable) {
            elem.classList.add('disabled', 'no-select');
            elem.disabled = true;
        } else {
            elem.classList.remove('disabled', 'no-select');
            elem.disabled = false;
        }
        elem.style.display = display;
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
        let duration = document.getElementById('runtimeDuration').value;
        fetch(this.url + '?action=2', {
            method: 'PUT',
            headers: json_headers,
            body: JSON.stringify({'duration': duration})
        }).then((response) => {
            if (response.ok){
                return response.json();
            }
        }).then((data) => {
            if (data['status'] === 200){
                this.getState(50);
            }
        });
    }
    stop(){
        this.toggle(51)
        fetch(this.url + '?action=4', {
            method: 'PUT'
        }).then((response) => {
            if (response.ok){
                return response.json();
            }
        }).then((data) => {
            if (data['status'] === 200) {
                this.getState(53);
            }
        });
    }
    extend(){
        fetch(this.url + '?action=10', {
            method: 'PUT'
        }).then((response) => {
            if (response.ok) {
                return response.json()
            }
        }).then(data => {
            if (data['status'] === 200){
                window.location.reload();
            }
        });
    }
    rebuild(servers=true){
        this.toggle(1, null, null, servers);
        fetch(this.url + '?action=1', {
            method: 'PUT'
        }).then((response) => {
            if (response.ok){
                return response.json();
            }
        }).then((data) => {
            if (data['status'] === 200) {
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
