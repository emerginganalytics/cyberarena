function previous_button(i) {
    i -= 1;
    window.location.href="/" + i;
}
function reset_assessment() {
    window.location.href="/0";
}

function print_results(){
    var original_contents = document.body.innerHTML;
    var printable_contents = document.getElementById('printable').innerHTML;
    document.body.innerHTML = printable_contents;
    window.print();
    document.body.innerHTML = original_contents;
}