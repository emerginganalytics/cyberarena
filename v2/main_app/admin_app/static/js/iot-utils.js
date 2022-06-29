function timeConverter(UNIX_timestamp){
    return new Date(UNIX_timestamp * 1000);
}
function disableField(targetField){
        targetField.prop("disabled", true);
        targetField.prop('hidden', true);
}
function enableField(targetField){
    targetField.prop('disabled', false);
    targetField.prop('hidden', false);
}