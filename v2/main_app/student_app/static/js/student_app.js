// Global Vars
var json_headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json; charset=UTF-8'
}
class TimestampToDate {
    constructor() {
        this.target_class = 'timestampField';
    }
    convert_timestamps(){
        let timestamp_list = document.getElementsByClassName(this.target_class);
        for (let i = 0; i < timestamp_list.length; i++){
            timestamp_list[i].innerHTML = this.timeConverter(timestamp_list[i].innerHTML);
        }
    }
    timeConverter(UNIX_timestamp){
        let a = new Date(UNIX_timestamp * 1000);
        let months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
        let year = a.getFullYear();
        let month = months[a.getMonth()];
        let date = a.getDate();
        let hour = a.getHours();
        let min = a.getMinutes();
        let sec = a.getSeconds();
        return date + ' ' + month + ' ' + year + ' ' + hour + ':' + min + ':' + sec ;
    }
}
function checkEscapeRoom(build_id, form_id, ea) {
    let puzzle_form = document.getElementById(form_id);
    let question_id = puzzle_form.querySelector('input[name="question_id"]').value;
    let response = puzzle_form.querySelector('input[name="response"]').value;
    var send_data = JSON.stringify({'build_id': build_id, 'response': response, 'question_id': question_id, 'ea': ea});

    const URL = '/api/escape-room/team/' + build_id;
    fetch(URL, {
        method: "PUT",
        headers: {'Content-Type': 'application/json'},
        body: send_data
    })
        .then((response) => response.json())
        .then(data=>console.log(data));
}
function showCurrentPuzzle(puzzle_idx) {
     $('#currentPuzzle' + puzzle_idx).modal();
}

