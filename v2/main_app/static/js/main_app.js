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
        let hour = a.getHours() % 12;
        let min = a.getMinutes();
        let sec = a.getSeconds();
        let format = a.getHours() >= 12 ? ' PM' : ' AM';
        if (hour < 10){
            hour = '0' + hour;
        }
        if (min < 10) {
            min = '0' + min;
        }
        if (!full){
            return month + '. ' + date + ' ' + hour + ':' + min + format;
        }
        return month + '. ' + date + ', ' + year + ' ' + hour + ':' + min + ':' + sec + format;
    }
}

function copyToClipboard(target_id, parentNode){
    /*
    * args:
    *   target_id (id of element to copy from )
    *   parentNode: id of element to create popup element in
    * */
    var copyText, copyPopup, node;
    // Copy text to clipboard
    copyText = document.getElementById(target_id).innerText;
    navigator.clipboard.writeText(copyText.trim());
    // Create copy confirm notif
    node = document.getElementById(parentNode);
    copyPopup = document.createElement('p');
    copyPopup.id = 'popup-notif-p';
    copyPopup.classList.add('popup-notif', 'fade-out', 'text-center');
    copyPopup.innerText = 'Copied to clipboard!';
    node.appendChild(copyPopup);
    setTimeout(function () {
        node.removeChild(copyPopup);
    }, 6000);
}