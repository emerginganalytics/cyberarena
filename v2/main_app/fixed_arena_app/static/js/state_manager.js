/*
* @author Andrew Bomberger
* @copyright Copyright 2022, UA Little Rock, Emerging Analytics Center
* @license MIT
* @since 1.0.0
* */
class StateManager {
    /*
    * Description.
    * This class is designed to be called on specific build actions such as
    * START, STOP, BUILD, DELETE and poll until the desired end state is reached.
    * Once the state is reached, the page will reload and stop the poll.
    *
    * In order to see the current states, make sure to include the .buildState class in
    * the desired HTML element. Recommended with a <div> tag.
    *
    * As each state is met, the element will be updated with
    * either:
    *    a color determined by states STOPPED, RUNNING, or this.bad_states
    * or:
    *    a Bootstrap tooltip for any other remaining state
    *
    * A loading animation can also be created by inserting the .loadAnimation class into
    * a div element.
    */
    constructor(build_type, build_id, end_state, auto_refresh=true) {
        this.build_type = build_type;
        this.build_id = build_id;
        this.end_state = end_state;
        this.auto_refresh = auto_refresh;
        this.old_state = '';
        this.bad_states = [60, 61, 62, 72];
        this.url = this.__getURL__();

        // Polling animation Boolean values
        this.waiting = false; // False if no wait animation was set
        this.table_animation = false; // False if no table animation was set
        this.create_class_animation = false; // False if no create class animation was set

        /* If check_multiple === false, __update_visuals__ will only update specified build
           (e.g. a single fixed-arena was started in table of existing fixed-arenas). */
        this.check_multiple = false;

    }
    getState(){
        // This method initiates state polling for basic build actions (START, STOP, etc)

        /* TODO: Need to update to handle monitoring multiple individual builds simultaneously
        *        Ideally, as each build completes, stop poll only for that build. Once all builds
        *        complete
        * */
        fetch(this.url, {
            method: 'GET',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json; charset=UTF-8'
            }
        })
            .then(response => response.json())
            .then((data) => {
                console.log(data);
                let result = this.__validate__(data);
                console.log('StateManager returned ' + result);
            })
            .catch(error => console.warn(error));
    }
    poll_create_stoc(table_id){
        /*
        * When resources are during build state, there will be a brief period of time when the build_id
        * doesn't exist yet. This
        * */
        // Create table load animation
        if (this.build_type === 2) {
            if (!this.table_animation){
                this.__table_row_animation__(table_id);
                this.table_animation = true;
            }
        } else if (this.build_type === 3) {
            fetch(this.url, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json; charset=UTF-8'
                }
            })
                .then(response => response.json())
                .then((data) => {
                    console.log(data);
                })
                .catch(error => console.warn(error));
        }
    }
    poll_create_class() {
        /* description.
        * - 1. Hide create class modal in fixed_arena.js
        * - 2. Check for build_id in fixed_arena['active_class']
        * - 3. If (active_class exists) => refresh page
        *   Else => wait 15s, poll again
        * */
        fetch(this.url, {
            method: 'GET',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json; charset=UTF-8'
            }
        })
            .then(response => response.json())
            .then((data) => {
                this.__waiting_animation__(data['state']);
                if (data['active_class' !== 'null'] && data['active_class'] !==  ''){
                    window.location.reload();
                } else {
                    this.__sleep__(100);
                    this.poll_create_class();
                }
            })
    }
    __getURL__(){
        if (this.build_type === 2){
            if (this.build_id > 1){
                // url to return list of all fixed-arenas in project
                return '/api/fixed-arena/';
            } else {
                // url to return state for single build
                return '/api/fixed-arena/' + this.build_id;
            }
        }
        else if (this.build_type === 3) {
            return '/api/fixed-arena/class/' + this.build_id;
        }
    }
    async __validate__(response){
        // Takes json object and validates data with desired end state
        // and determines the next solution
        if (response['status'] === 200){
            if (!this.check_multiple) {
                if (response['data']['state'] === this.end_state) {
                    // Build action is completed successfully;
                    if (this.auto_refresh) {
                        // Reload page to see changes
                        window.location.reload();
                    } else {
                        this.__updateVisuals__(response['data']['state'])
                        return true;
                    }
                } else if (response['data']['state'] === 72) {
                    // Build is no longer exists; Update visuals and stop Polling
                    this.__updateVisuals__(response['data']['state']);
                    return false;
                } else {
                    // Build action is not complete; Wait 30s before checking again
                    this.__updateVisuals__(response['data']['state']);
                    await this.__sleep__(30000)
                        .then(() => {
                            this.getState();
                        });
                }
            } else {
                let resp_data = response['data'];
                for (let i = 0; i < resp_data.length; i++){
                    this.__updateVisuals__(resp_data[i]['state'], resp_data[i]['id']);
                }
            }
        }
    }
    __updateVisuals__(state, build_id=null){
        /*
        * Looks for the following classes in the current page and updates them accordingly based on current state
        *   target tooltip class: .buildState
        * target load animation class: .loadAnimationWrapper
        *
        * If state is not a transition state, halt loadAnimation
        *
        * If build_id is provided in method call, update visual for specific row with matching
        *   parent_id = build_id + 'StatusDiv'
        * */
        let msg = '';
        let status_dot = '';
        var buildIdDiv = '';
        if (build_id) {
            buildIdDiv = build_id + 'StatusDiv';
        }

        if (state !== this.old_state) {
            let status_dots = document.getElementsByClassName('buildState');
            // If the state has changed, update visuals with appropriate class
            if (state === 50) {
                msg = 'RUNNING';
                status_dot = 'running';
            } else if (state === 53) {
                msg = 'STOPPED';
                status_dot = 'stopped'
            } else if (this.bad_states.includes(state)) {
                if (state === 72){
                    msg = 'DELETED';
                } else {
                    msg = 'BROKEN';
                }
                status_dot = 'deleted'
            } else {
                status_dot = 'transition'
                msg = 'WORKING';
            }
            for (let i = 0; i < status_dots.length; i++){
                let current_dot = status_dots[i];
                if (build_id) {
                    if (current_dot.parentElement.id !== buildIdDiv) {
                        // Current element does not match requested build_id, ignore update request
                        continue;
                    }
                }
                // Clear any old states first
                current_dot.classList.remove('running', 'stopped', 'deleted', 'transition');
                // Add new state class
                current_dot.classList.add(status_dot);
                // Update tooltip title
                current_dot.setAttribute('title', msg);
                current_dot.setAttribute('data-original-title', msg);
                current_dot.setAttribute('tooltip', 'update');
                current_dot.setAttribute('tooltip', 'show');
            }
            this.__waiting_animation__(state);
            this.old_state = state;
        }
    }
    __waiting_animation__(state){
        // If animation is not already created, insert class
        if (!this.waiting){
            let loadElem = $('.loadAnimationWrapper').find('#loadAnimation');
            if (!(state === this.end_state)) {
                loadElem.addClass('loadAnimation');
                // Set waiting to true to avoid triggering the animation multiple times
                this.waiting = true;
            } else {
                // End state met; Remove animation
                loadElem.classList.remove('loadAnimation');
                this.waiting = false;
            }
        }
    }
    __table_row_animation__(table_id){
        let table = document.getElementById("" + table_id);
        let row = table.insertRow(0);
        let cells = $('#' + table_id).find('th').length
        for (let i = 0; i < cells; i++){
            let new_cell = row.insertCell(i);
            new_cell.classList.add('table-row-animation');
        }
    }
    __sleep__(ms){
        return new Promise(resolve => setTimeout(resolve, ms));
    }
} // End StateManager class
// [ eof ]
