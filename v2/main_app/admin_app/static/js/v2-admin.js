var json_headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json; charset=UTF-8'
}
function filterEmails(){
    var input, filter, table, tr, td, i, tdValue;
    input = document.getElementById('searchEmail');
    filter = input.value.toLowerCase();
    table = document.getElementById('admin-users-table');
    tr = table.getElementsByTagName('tr');

    for (i = 0; i < tr.length; i++){
        td = tr[i].getElementsByTagName("td")[2];
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
            td = tr[i].getElementsByTagName('td')[3];
            if (td){
                groupDivs = td.getElementsByTagName('div');
                if (groupDivs){
                    for (j = 0; j < groupDivs.length; j++) {
                        group = groupDivs[j];
                        if (filter === group.textContent.toLowerCase()){
                            tr[i].style.display = "";
                            break;
                        } else {
                            tr[i].style.display = 'none';
                        }
                    }
                }
            }
        }
    }
}
function manage_user(uid){
    let manageForm, user_modal, user, pending, groups, admin, instructor, student, approve;
    user_modal = $('#' + uid + 'Modal').modal('toggle');
    manageForm = document.getElementById(uid + 'ManageForm');
    if (manageForm){
        user = manageForm.elements['user'].value;
        pending = manageForm.elements['currentLevel'].value;
        approve = true;
        if (pending === 'pending'){
            approve = manageForm.elements['approve'].checked;
            if (approve){
                groups = {
                    'admin': manageForm.elements['admin'].checked,
                    'instructor': manageForm.elements['instructor'].checked,
                    'student': manageForm.elements['student'].checked,
                }
            } else {
                groups = {
                    'admin': false,
                    'instructor': false,
                    'student': false
                }
            }
        } else {
            admin = manageForm.elements['admin'].checked;
            instructor = manageForm.elements['instructor'].checked;
            student = manageForm.elements['student'].checked;
            groups = {
                'admin': admin,
                'instructor': instructor,
                'student': student
            }
        }
        let payload = {
            'groups': groups,
            'pending': pending,
            'user': user,
            'approve': approve
        }
        fetch('/api/user', {
            method: 'POST',
            headers: json_headers,
            body: JSON.stringify(payload)
        })
            .then(response => response.json())
            .then(data => {
                if (data['status'] === 200){
                    window.location.reload();
                } else {
                    console.log(data);
                }
            });
    }
}
function add_user(form_id, modal_id){
    let userForm, user_modal, user, groups, admin, instructor, student, payload;
    user_modal = $('#' + modal_id).modal('toggle');
    userForm = document.getElementById(form_id);
    groups = {
        'admin': userForm.elements['admin'].checked,
        'instructor': userForm.elements['instructor'].checked,
        'student': userForm.elements['student'].checked
    }
    user = userForm.elements['new_user'].value;
    payload = {
        'groups': groups,
        'new_user': user,
    }
    fetch('/api/user', {
        method: 'POST',
        headers: json_headers,
        body: JSON.stringify(payload)
    })
        .then(response => response.json())
        .then(data => {
            if (data['status'] === 200){
                window.location.reload();
            } else {
                console.log(data);
            }
        });
}
function enableGroups(enable, uid){
    let groups = ['checkAdmins', 'checkInstructor', 'checkStudents'];
    groups.forEach((group) => {
        let obj = document.getElementById(group + '-' + uid);
        if (enable){
            obj.removeAttribute('disabled');
        } else {
            obj.setAttribute('disabled', 'true');
        }
    });
}
function filter_active_units(){
    var input, filter, table, tr, td, i, tdValue, filterType, col;
    input = document.getElementById('searchUnits');
    filter = input.value.toLowerCase();
    filterType = document.getElementById('filterUnitsCol').value;
    table = document.getElementById('active-units-table');
    tr = table.getElementsByTagName('tr');
    col = 1;
    if (filterType === 'filterByID'){
        col = 1;
    } else if (filterType === 'filterByJoinCode') {
        col = 4;
    }
    for (i = 0; i < tr.length; i++){
        td = tr[i].getElementsByTagName("td")[col];
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