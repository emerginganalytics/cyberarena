class Control {
    /*
    * Params:
    *   build_id: String() referencing ID of workout to send action for
    *   elem_id: String() referencing ID of target HTML element containing state
    *       UI objects
    * */
    constructor(build_id = null, elem_id = null, url = null) {
        this.build_id = build_id;
        this.elem_id = elem_id;
        this.url = url + build_id;
        this.urlWithState = this.url + '?state=true';
        this.jsonHeaders = {
            'Content-Type': 'application/json'
        };

        this.updateState = this.updateState.bind(this);
    }


    updateState(state) {
        const nextState = this.nextState;
        let stateObj = document.getElementById(this.elem_id);

        if (state === nextState || state === '72' || state === '62') {
            window.location.reload();
        } else {
            stateObj.classList.add('transition');
            stateObj.classList.remove('running', 'stopped', 'deleted', 'broken', 'notbuilt');
        }
    }

    getState(nextState) {
        this.nextState = nextState;
        const url = this.urlWithState;

        setInterval(() => {
            fetch(url, {
                method: 'GET'
            }).then((response) => response.json())
              .then((data) => {
                  const state = data?.data?.state;
                  this.updateState(state);
              });
        }, 5000);
    }

    toggle(state, func1 = null, func2 = null, servers = true) {
        const disableElement = func1 !== null && func2 !== null ? func1 : this.disableElement;
        const disableElements = func1 !== null && func2 !== null ? func2 : this.disableElements;

        let startWorkoutLi = document.getElementById('startWorkoutLi') || null;
        let startButton = document.getElementById('startWorkoutBtn') || null;
        let stopButton = document.getElementById('stopWorkoutBtn') || null;
        let workoutStateObj = document.getElementById('workoutStateObj');
        let workoutStateIcon = document.getElementById('workoutState');
        let connectionBtns = document.getElementsByClassName('connection-link') || [];
        let extendWorkoutLi = document.getElementById('extendWorkoutLi') || null;
        let extendDurationBtn = document.getElementById('extendDurationBtn') || null;
        let roomTimerDiv = document.getElementById('room-timer-div') || null;
        let roomTimerInput = document.getElementById('runtimeDuration') || null;
        let loadingIcon = null;

        if (state === 1) {
            const rebuildBtn = document.getElementById('rebuildWorkoutBtn');
            loadingIcon = rebuildBtn.querySelector('.loading-icon');
            loadingIcon.classList.add('animated');
            disableElement(rebuildBtn, true);
            workoutStateObj.innerText = 'WORKING';
            workoutStateIcon.classList.remove('stopped', 'running', 'broken', 'notbuilt');
            workoutStateIcon.classList.add('transition');
            disableElement(workoutStateObj);
            if (servers) {
                disableElement(stopButton);
                disableElement(startButton);
            }
        } else if (state === 50) {
            workoutStateObj.innerText = 'RUNNING';
            workoutStateIcon.classList.remove('transition', 'stopped');
            workoutStateIcon.classList.add('running');
            disableElement(roomTimerDiv, false, 'block');
            disableElement(roomTimerInput, true, 'none');
            if (servers) {
                disableElement(workoutStateObj, false);
                disableElement(stopButton, false);
                disableElement(startButton, true, 'none');
                disableElement(startWorkoutLi, true, 'none');
                disableElement(extendDurationBtn, false);
                disableElements(extendWorkoutLi, false);
            }
            disableElements(connectionBtns, false, disableElement);
        } else if (state === 53) {
            workoutStateObj.innerText = 'STOPPED';
            workoutStateIcon.classList.remove('transition', 'running');
            workoutStateIcon.classList.add('stopped');
            disableElement(workoutStateObj);
            disableElement(roomTimerDiv, true, 'none');
            disableElement(roomTimerInput, false);
            disableElement(stopButton);
            disableElement(startButton, false);
            disableElement(startWorkoutLi, false);
            disableElement(extendDurationBtn, true, 'none');
            disableElement(extendWorkoutLi, true, 'none');
            disableElements(connectionBtns, true, disableElement);
        } else if (state === 72) {
            workoutStateObj.innerText = 'DELETED';
            workoutStateIcon.classList.remove('transition', 'running', 'stopped');
            workoutStateIcon.classList.add('deleted');
            disableElement(workoutStateObj);
            disableElement(roomTimerDiv, true, 'none');
            disableElement(roomTimerInput, true, 'none');
            disableElement(stopButton);
            disableElement(startButton, false);
            disableElement(extendDurationBtn, true, 'none');
            disableElement(extendWorkoutLi, true, 'none');
            disableElements(connectionBtns, true, disableElement);
        } else if (state === 62) {
            workoutStateObj.innerText = 'BROKEN';
            workoutStateIcon.classList.remove('transition', 'running', 'stopped');
            workoutStateIcon.classList.add('broken');
            disableElement(workoutStateObj);
            disableElement(roomTimerDiv, true, 'none');
            disableElement(roomTimerInput, true, 'none');
            disableElement(stopButton, false);
            disableElement(startButton);
            disableElement(extendDurationBtn, true, 'none');
            disableElement(extendWorkoutLi, true, 'none');
            disableElements(connectionBtns, true, disableElement);
        } else {
            workoutStateObj.innerText = 'WORKING';
            workoutStateIcon.classList.remove('stopped', 'running', 'broken', 'notbuilt');
            workoutStateIcon.classList.add('transition');
            disableElement(workoutStateObj);
            disableElement(roomTimerDiv, true, 'block');
            disableElement(roomTimerInput, true, true);
            disableElement(stopButton);
            disableElement(startButton);
            disableElement(extendDurationBtn, true, 'none');
            disableElement(extendWorkoutLi, true, 'none');
            disableElements(connectionBtns, true, disableElement);
        }
    }

    disableElement(elem, disable = true, display = 'inline') {
        if (disable) {
            elem.classList.add('disabled', 'no-select');
            elem.disabled = true;
        } else {
            elem.classList.remove('disabled', 'no-select');
            elem.disabled = false;
        }
        elem.style.display = display;
    }

    disableElements(elems, disable = true, disableElement) {
        for (let i = 0; i < elems.length; i++) {
            disableElement(elems[i], disable);
        }
    }

    start() {
        this.toggle(52);
        const duration = document.getElementById('runtimeDuration').value;
        const requestBody = {
            duration: duration
        };

        fetch(this.url + '?action=2', {
            method: 'PUT',
            headers: this.jsonHeaders,
            body: JSON.stringify(requestBody)
        }).then((response) => {
            if (response.ok) {
                return response.json();
            }
        }).then((data) => {
            if (data?.status === 200) {
                this.getState(50);
            }
        });
    }

    stop() {
        this.toggle(51);
        fetch(this.url + '?action=4', {
            method: 'PUT'
        }).then((response) => {
            if (response.ok) {
                return response.json();
            }
        }).then((data) => {
            if (data?.status === 200) {
                this.getState(53);
            }
        });
    }

    extend() {
        fetch(this.url + '?action=10', {
            method: 'PUT'
        }).then((response) => {
            if (response.ok) {
                return response.json();
            }
        }).then((data) => {
            if (data?.status === 200) {
                window.location.reload();
            }
        });
    }

    rebuild(servers = true) {
        this.toggle(1, null, null, servers);
        fetch(this.url + '?action=1', {
            method: 'PUT'
        }).then((response) => {
            if (response.ok) {
                return response.json();
            }
        }).then((data) => {
            if (data?.status === 200) {
                this.getState(53);
            }
        });
    }

    poll() {
        const url = this.urlWithState;
        setInterval(() => {
            fetch(url, {
                method: 'GET'
            }).then((response) => response.json())
              .then((data) => {
                  const state = data?.data?.state;
                  this.toggle(state, this.disableElement, this.disableElements);
              });
        }, 300000);
    }
}
