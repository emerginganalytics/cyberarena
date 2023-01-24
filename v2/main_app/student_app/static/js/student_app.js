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
            timestamp_list[i].innerHTML = this.timeConverter(timestamp_list[i].innerHTML, false);
        }
    }
    timeConverter(UNIX_timestamp, full=true){
        let a = new Date(UNIX_timestamp * 1000);
        let months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
        let year = a.getFullYear();
        let month = months[a.getMonth()];
        let date = a.getDate();
        let hour = a.getHours();
        let min = a.getMinutes();
        let sec = a.getSeconds();
        if (!full){
            return month + ' ' + date + ' ' + hour + ':' + min;
        }
        return month + ' ' + date + ', ' + year + ' ' + hour + ':' + min + ':' + sec ;
    }
}
function getEscapeRoomState (build_id){
    // Checks current escape_room status every 5 minutes and updates
    // the page as needed
    const URL = '/api/escape-room/team/' + build_id + '?status=true';
    setInterval(function() {
        $.ajax({
            url: URL,
            type: 'get',
            success: function (data){
                let toJson = JSON.parse(data);
                console.log(toJson);
                checkPuzzles(toJson['status'], toJson['data']);
            }
        })
    }, 300000);
}
function checkEscapeRoom(build_id, form_id, puzzle_idx, ea) {
    showCurrentPuzzle(puzzle_idx);
    const URL = '/api/escape-room/team/' + build_id;
    let puzzle_form = document.getElementById(form_id);
    let question_id = puzzle_form.querySelector('input[name="question_id"]').value;
    let response = puzzle_form.querySelector('input[name="response"]').value;
    let send_data = JSON.stringify({'build_id': build_id, 'response': response, 'question_id': question_id, 'ea': ea});
    fetch(URL, {
        method: "PUT",
        headers: {'Content-Type': 'application/json'},
        body: send_data
    })
        .then((response) => response.json())
        .then(data=>checkPuzzles(data['status'], data['data']));
}
function checkPuzzles(code, responseData){
    if (code === 200){
        console.log('Updating Room Status ...');
        let room = responseData['escape_room'];
        let number_correct = room['number_correct'];
        let puzzle_count = room['puzzle_count'];
        if (number_correct !== puzzle_count){
            for (let i = 0; i < room['puzzles'].length; i++){
                let puzzle = room['puzzles'][i];
                console.log(puzzle);
                if (puzzle['correct'] === true){
                    let reveal = document.getElementById(puzzle['id'] + '-reveal');
                    reveal.innerText = puzzle['reveal'];
                }
            }
        } else {
            window.location.reload();
        }
    }
}
function showCurrentPuzzle(puzzle_idx) {
     $('#currentPuzzle' + puzzle_idx).modal('toggle');
}
function collapseDiv(){
    let coll = document.getElementsByClassName("collapseBtn");
    for (let i = 0; i < coll.length; i++) {
        coll[i].addEventListener("click", function() {
            this.classList.toggle("collapse-active");
            let content = this.nextElementSibling;
            console.log(content.id);
            if (content.style.display === "block") {
                content.style.display = "none";
            } else {
                content.style.display = "block";
            }
        });
    }
}
