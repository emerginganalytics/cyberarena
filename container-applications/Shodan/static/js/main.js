function view_raw_data(rawData){
    myWindow = window.open(rawData);
    myWindow.document.write(rawData);
    console.log(rawData);

}