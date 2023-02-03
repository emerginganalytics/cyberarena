// Global Vars
var json_headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json; charset=UTF-8'
}
function getEscapeRoomState (build_id, ts=300000, started=true){
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
                if (Number(toJson['data']['escape_room']['start_time']) > 0){
                    if (started) {
                        checkPuzzles(toJson['status'], toJson['data']);
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
            addClass(this);
            let content = this.nextElementSibling;
            if (content.style.display === "block") {
                content.style.display = "none";
            } else {
                content.style.display = "block";
            }
        });
    }
    function addClass(parent){
        let iconSpan = parent.querySelectorAll(':scope > span')[0];
        // Add the element based on parent element class
        if (parent.classList.contains('collapse-active')){
            iconSpan.innerHTML = '<i class="fa fa-minus" aria-hidden="true"></i>';
        } else {
            iconSpan.innerHTML = '<i class="fa fa-angle-down" aria-hidden="true"></i>';
        }
    }
}
function checkQuestion(questionID, build_id, url){
    let question_form = document.getElementById(questionID + 'Form');
    let response = question_form.querySelector('input[name="response"]').value;
    let parent_id = question_form.querySelector('input[name="parent_id"]').value;
    let send_data = JSON.stringify({'build_id': build_id, 'response': response, 'question_id': questionID});
    fetch(url, {
        method: 'PUT',
        headers: json_headers,
        body: send_data
    })
        .then((response) => response.json())
        .then(data=>updateQuestions(data['status'], data['data']));
}
function updateQuestions(code, responseData){
    // updates all question fields upon request
    // TODO: Existing question states will be assigned during each successful window.reload() via templating
    if (code === 200){
        for (let i = 0; i < responseData['questions'].length; i++){
            let item = document.getElementById(i['id'] + 'Btn');
            if (i['complete'] === true){
                i.style.display = 'none';
            } else if (i['complete'] === false){
                item.classList.add('incomplete');
            }
        }
    }
}