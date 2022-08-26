/*
* @author Andrew Bomberger
* @copyright Copyright 2022, UA Little Rock, Emerging Analytics Center
* @license MIT
* @since 1.0.0
* */
class StateChecker {
    /*
    * Description.
    * This class is designed to be called on specific build actions such as
    * START, STOP, BUILD, DELETE and poll until the desired end state is reached.
    * Once the state is reached, the page will reload and stop the poll.
    *
    * In order to see the current states, make sure to include the .buildState class in
    * the desired HTML element. Recommended element is either an <i> or <span> tag.
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
    constructor(build_type, build_id, end_state) {
        this.build_type = build_type;
        this.build_id = build_id;
        this.end_state = end_state;
        this.old_state = '';
        this.bad_states = [60, 61, 62, 72];
        this.url = this.__getURL__();
        this.waiting = false; // False if no wait animation was set
    }
    getState(){
        // Call this method to initiate state polling
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
                this.__validate__(data);
            })
            .catch(error => console.warn(error));
    }
    __getURL__(){
        if (this.build_type === 2){
            return '/api/fixed-arena/' + this.build_id;
        }
        else if (this.build_type === 3) {
            return '/api/fixed-arena/class/' + this.build_id;
        }
    }
    async __validate__(response){
        // Takes json object and validates data with desired end state
        // and determines the next solution
        if (response['status'] === 200){
            if (response['data']['state'] === this.end_state){
                // Build action is completed successfully; Reload page to see changes
                window.location.reload();
            } else if (response['data']['state'] === 72) {
                // Build is no longer exists; Update visuals and stop Polling
                this.__updateVisuals__(response['data']['state']);
                return false;
            } else {
                // Build action is not complete; Wait 30s before checking again
                this.__updateVisuals__(response['data']['state']);
                await this.__sleep__(300)
                    .then(() => {
                        this.getState()
                    });
            }
        }
    }
    __updateVisuals__(state){
        /*
        * Looks for the following classes in the current page and updates them accordingly based on current state
        *   target tooltip class: .buildState
        * target load animation class: .loadAnimationWrapper
        *
        * If state is not a transition state, halt loadAnimation
        * */
        let msg = '';
        let status_dot = '';

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
                // clear any old states first
                status_dots[i].classList.remove('running', 'stopped', 'deleted', 'transition');
                // add new state class
                status_dots[i].classList.add(status_dot);
                // update tooltip title
                status_dots[i].setAttribute('title', msg);
                status_dots[i].setAttribute('data-original-title', msg);
                status_dots[i].setAttribute('tooltip', 'update');
                status_dots[i].setAttribute('tooltip', 'show');
            }
            // If this is the first time running, init the load animation
            if (!(this.waiting)) {
                let loadElem = $('.loadAnimationWrapper').find('#loadAnimation');
                loadElem.addClass('loadAnimation');
                // set waiting to true to avoid triggering the animation multiple times
                this.waiting = true;
            }
            this.old_state = state;
        }
    }
    __sleep__(ms){
        return new Promise(resolve => setTimeout(resolve, ms));
    }
} // End StateChecker
// [ eof ]