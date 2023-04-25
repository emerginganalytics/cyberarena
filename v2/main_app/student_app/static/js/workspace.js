class WorkspaceControl {
    constructor(build_id=null, elem_id=null, url=null) {
        this.build_id = build_id;
        this.elem_id = elem_id;
        this.url = url + build_id;
    }
    toggle(state, func1=null, func2=null){
        let stateText, stateObj, control, stateIcon;
        stateObj = document.getElementById('workoutStateObj');
        stateIcon = document.getElementById('workoutState');

        if (state === 50){
            stateObj.innerText = 'RUNNING';
            stateIcon.classList.remove('transition', 'stopped');
            stateIcon.classList.add('running');
        } else if (state === 53){
            stateObj.innerText = 'STOPPED';
            stateIcon.classList.remove('transition', 'running');
            stateIcon.classList.add('stopped');
        } else if (state === 62){
            stateObj.innerText = 'BROKEN';
            stateIcon.classList.remove('transition', 'running', 'stopped');
            stateIcon.classList.add('broken');
        } else if (state === 72){
            stateObj.innerText = 'DELETED';
            stateIcon.classList.remove('transition', 'running', 'stopped');
            stateIcon.classList.add('deleted');
        } else {
            stateObj.innerText = 'WORKING'
            stateIcon.classList.remove('stopped', 'running');
            stateIcon.classList.add('transition');
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