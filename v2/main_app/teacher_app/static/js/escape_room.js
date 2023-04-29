class EscapeRoom {
    constructor(build_id=null, url=null, elem_id=null) {
        this.build_id = build_id;
        this.url = url + this.build_id
        this.elem_id = elem_id;
    }
    getURL(url, build_id){
        return url + build_id;
    }
    updateStateObj(stateObjects, state){
        let states = {53: 'STOPPED', 50: 'RUNNING', 72: 'DELETED'}
        let stateList = ['running', 'stopped', 'transition', 'deleted']
        for (let i=0; i < stateObjects.length; i++){
            stateObjects[i].classList.remove(...stateList);
            if (state in states){
                stateObjects[i].classList.add(String(states[state]).toLowerCase());
            } else {
                stateObjects[i].classList.add('transition');
            }
        }
    }
    toggle(state){
        let startBtn, startTime, icon, buildStateObjs;
        buildStateObjs = document.getElementsByClassName('buildState');
        if (state !== 9){
            this.updateStateObj(buildStateObjs, state);
        }
        if (state === 52){
            startTime = document.getElementById('startEscapeRoomTimer');
            startTime.classList.remove('disabled');
            startBtn = document.getElementById('startEscapeRoomBtn');
            startBtn.classList.add('disabled');
            icon = startBtn.querySelector('.loading-icon');
            icon.classList.add('animated');
        } else if (state === 53) {
            startTime = document.getElementById('startEscapeRoomTimer');
            startTime.classList.add('disabled');
            startBtn = document.getElementById('startEscapeRoomBtn');
            startBtn.classList.remove('disabled');
            icon = startBtn.querySelector('.loading-icon');
            icon.classList.remove('animated');
        } else if (state === 9){
            startTime = document.getElementById('startEscapeRoomTimer');
            startTime.classList.add('disabled');
            startBtn = document.getElementById('startEscapeRoomBtn');
            startBtn.classList.add('disabled');
            icon = startBtn.querySelector('.loading-icon');
            icon.classList.remove('animated');
        } else if (state === 50) {
            startTime = document.getElementById('startEscapeRoomTimer');
            startTime.classList.remove('disabled');
            startBtn = document.getElementById('startEscapeRoomBtn');
            startBtn.classList.add('disabled');
            icon = startBtn.querySelector('.loading-icon');
            icon.classList.remove('animated');
        }
    }
    startMachines(){
        let build_id = this.build_id;
        let startMachineBtn, startTimerBtn, controlGroupDiv, loadingIcon, json_data;
        this.toggle(52);
        json_data = JSON.stringify({'unit_action': 2, 'build_id': build_id});
        fetch(this.url, {
            method: 'PUT',
            headers: json_headers,
            body: json_data
        }).then(response =>
            response.json()
        ).then((data) =>{
            console.log(data);
            if (data['status'] === 200){
                this.updateStateObj()
                this.getState(50);
            }
        });
    }
    startTimer(){
        this.toggle(9);
        let json_data = JSON.stringify({'unit_action': 9, 'build_id': this.build_id});
        fetch(this.url, {
            method: 'PUT',
            headers: json_headers,
            body: json_data
        }).then(response =>
            response.json()
        ).then((data) =>{
            if (data['status'] === 200) {
                window.location.reload();
            }
        });
    }
    getState(nextState){
        console.log('Starting state poll ...');
        let url = this.url + '?state=true';
        function updateState(state){
            if (state === nextState || state === '72' || state === '62'){
                window.location.reload();
            }
        }
        setInterval(function (){
            fetch(url, {
                method: 'GET'
            }).then((response) =>
                response.json()
            ).then((data) => {
                let states = data['data']['states'];
                let current_state = Math.max(...states);
                console.log('Current State: ' + current_state);
                updateState(current_state);
            });
        }, 15000); // 15000; 5min => 300000
    }
    poll(build_id, ts=300000, started=true){
        // Checks current escape_room status every 5 minutes and updates
        // the page as needed
        const URL = '/api/escape-room/team/' + build_id + '?status=true';
        let checkEscapeRoomPuzzles = this.checkEscapeRoomPuzzles;
        setInterval(function() {
            $.ajax({
                url: URL,
                type: 'get',
                success: function (data){
                    let toJson = JSON.parse(data);
                    if (Number(toJson['data']['escape_room']['start_time']) > 0){
                        if (started) {
                            checkEscapeRoomPuzzles(toJson['status'], toJson['data']);
                        } else {
                            window.location.reload();
                        }
                    } else {
                        console.log('...Not started');
                    }
                }
            })
        }, ts);
    }
    checkEscapeRoomPuzzles(code, responseData, puzzle_idx){
        if (code === 200){
            console.log('Updating Room Status ...');
            let room = responseData['escape_room'];
            let number_correct = room['number_correct'];
            let puzzle_count = room['puzzle_count'];
            if (number_correct !== puzzle_count){
                for (let i = 0; i < room['puzzles'].length; i++){
                    let puzzle = room['puzzles'][i];
                    if (puzzle['correct'] === true){
                        let card = document.getElementById('puzzle-' + puzzle_idx + '-status').innerText = 'Complete!';
                        let reveal = document.getElementById(puzzle['id'] + '-reveal');
                        reveal.innerText = puzzle['reveal'];
                    }
                }
            } else {
                window.location.reload();
            }
        }
    }
}