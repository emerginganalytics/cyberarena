function filterEmails(){
    var input, filter, table, tr, td, i, tdValue;
    input = document.getElementById('searchEmail');
    filter = input.value.toLowerCase();
    table = document.getElementById('admin-users-table');
    tr = table.getElementsByTagName('tr');

    for (i = 0; i < tr.length; i++){
        td = tr[i].getElementsByTagName("td")[1];
        if (td) {
            tdValue = td.textContent || td.innerText;
            if (tdValue.toLowerCase().indexOf(filter) > -1){
                tr[i].style.display = "";
            } else {
                tr[i].style.display = "none";
            }
        }
    }
}
function filterGroup(filter_group){
    var group, filter, table, tr, td, i, j, groupDivs, divValue;
    filter = filter_group.toLowerCase();
    table = document.getElementById('admin-users-table');
    tr = table.getElementsByTagName('tr');
    for (i = 0; i< tr.length; i++){
        if (filter === 'all'){
            tr[i].style.display = '';
        } else {
            td = tr[i].getElementsByTagName('td')[2];
            if (td){
                groupDivs = td.getElementsByTagName('div');
                if (groupDivs){
                    for (j = 0; j < groupDivs.length; j++) {
                        group = groupDivs[j];
                        if (filter === group.textContent.toLowerCase()){
                            tr[i].style.display = "";
                        } else {
                            tr[i].style.display = 'none';
                        }
                    }
                }
            }
        }
    }
}