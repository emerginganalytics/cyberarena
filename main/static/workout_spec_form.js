function prepare_workout_form(){
    var build_type_select = document.getElementById("build_type_select");
    build_type_select.addEventListener("change", function(){
        if(this.value == "compute"){
            document.getElementById("compute_build_form").style.display = "block";
            document.getElementById("container_build_form").style.display = "none";
        }
        else if(this.value == "container"){
            document.getElementById("compute_build_form").style.display = "none";
            document.getElementById("container_build_form").style.display = "block";
        }
    })

    /*document.getElementById('new_workout_form').addEventListener('submit', function(event){
        event.preventDefault();
        var formData = new FormData(this);
        var test = new FormData();
        var teacher_file = document.getElementById('teacher_instruction_file').files;
    });*/

}

function get_workout_form_data(){
    var data = {};
    data['workout'] = [];

    //Get basic workout info
    var workout_info = {};
    workout_info['name'] = document.getElementById('workout_name').value;
    var build_type = document.getElementById('build_type_select').value;
    workout_info['build_type'] = build_type;
    workout_info['workout_description'] = document.getElementById('workout_description').value;

    data['workout'] = workout_info;
    
    if(build_type == "compute"){
        //Process Networks
        var networks = document.getElementsByClassName('network_info_container');
        for(var i = 0; i < networks.length; i++){
            var network_info = {};
            var network_div = networks[i];

            var network_name = network_div.querySelector(".network_name");
            network_info['name'] = network_name.value;

            var network_subnets = network_div.getElementsByClassName('subnet_group');
            var subnets = [];
            for(var j = 0; j < network_subnets.length; j++){
                var ip = network_subnets[j].querySelector('.subnet_ip');
                var name = network_subnets[j].querySelector('.subnet_name');
                var subnet_info = {};
                subnet_info['ip_subnet'] = ip.value;
                subnet_info['name'] = name.value;
                subnets[j] = subnet_info;
            }
            network_info['subnets'] = subnets;
            if(!data['networks']){
                data['networks'] = [];
            }
            data['networks'][i] = network_info;
            
        }

        //Process Servers
        var servers = document.getElementsByClassName('server_info_container');

        for(var i = 0; i < servers.length; i++){
            var server_info = {};
            var server_div = servers[i];

            var server_name = server_div.querySelector('.server_name');
            server_info['name'] = server_name.value;

            //Server Tags
            var server_tags = server_div.getElementsByClassName('server_tag');
            var tags = {items: []};

            for(var j = 0; j < server_tags.length; j++){
                tags.items.push(server_tags[j].value);
            }

            
            //Server NICS
            var server_nics = server_div.getElementsByClassName('nic_group');
            var nics = [];
            for(var j = 0; j < server_nics.length; j++){
                var nic_ip = server_nics[j].querySelector('.nic_internal_ip');
                var nic_network = server_nics[j].querySelector('.nic_network_select');
                var nic_info = {};

                nic_info['internal_ip'] = nic_ip.value;
                nic_info['network'] = nic_network.value;
                nics[j] = nic_info;
            }
            server_info['nics'] = nics;
            if(tags['items'].length !== 0){
                server_info['tags'] = tags;
            }
            if(!data['servers']){
                data['servers'] = [];
            }
            data['servers'][i] = server_info;
        }
        
        //Process Student Entry
        var student_entry = {};
        student_entry['type'] = document.getElementById('student_entry_type').value;
        student_entry['username'] = document.getElementById('workout_username').value;
        student_entry['password'] = document.getElementById('workout_password').value;
        student_entry['ip'] = document.getElementById('host_ip_select').value;
        student_entry['network'] = document.getElementById('student_entry_select').value;

        if(!data['student_entry']){
            data['student_entry'] = []
        }
        data['student_entry'][0] = student_entry;

        //Process Firewalls
        var firewalls = document.getElementsByClassName('firewall_info_container');

        for(var i = 0; i < firewalls.length; i++){
            var firewall_info = {};
            var firewall_div = firewalls[i];

            var firewall_name = firewall_div.querySelector('.firewall_name');
            firewall_info['name'] = firewall_name.value;

            var firewall_protocol = firewall_div.querySelector('.firewall_protocol')
            firewall_info['protocol'] = firewall_protocol.value;

            var firewall_network = firewall_div.querySelector('.firewall_network_select');
            firewall_info['network'] = firewall_network.value;

            var firewall_server_tag = firewall_div.querySelector('.firewall_tag_select');
            firewall_info['target_tags'] = [];
            firewall_info['target_tags'].push(firewall_server_tag.value);
            if(!data['firewalls']){
                data['firewalls'] = [];
            }
            data['firewalls'][i] = firewall_info;
        }
    }else{
        //Process container workout info
        var container_url = document.getElementById('container_url').value;
        data['workout']['container_url'] = container_url;
    }
    //Process Assessment
    var assessment = document.getElementsByClassName('assessment_item');

    for(var i = 0; i < assessment.length; i++){
        question_info = {};
        question_div = assessment[i];

        var assessment_type = question_div.querySelector('.question_type');
        question_info['type'] = assessment_type.value;

        var assessment_question = question_div.querySelector('.question_text');
        question_info['question'] = assessment_question.value;

        var assessment_answer = question_div.querySelector('.answer');
        question_info['answer'] = assessment_answer.value;

        if(!data['assessment']){
            data['assessment'] = [];
        }
        data['assessment'][i] = question_info;
    }
    return data;
}
function process_new_spec(){
    //Send data to server to generate a yaml document
    var data = get_workout_form_data();
    $.ajax({
        type:"POST",
        url: "/admin/api/create_workout_spec",
        data: JSON.stringify(data),
        contentType: "application/json;charset=utf-8",
        success: function(response){
            
            var yaml_content_div = document.getElementById('yaml_content');
            while(yaml_content_div.firstChild){
                yaml_content_div.removeChild(yaml_content_div.firstChild);
            }
            var json = $.parseJSON(response)
            var yaml_content = document.createElement('p');
            yaml_content_div.appendChild(yaml_content);
            for(var i = 0; i < json['content_list'].length; i++){
                var line = json['content_list'][i];
                var line_element = document.createElement('pre');
                line_element.innerHTML = line;
                yaml_content_div.append(line_element);
            }

            $('#yaml_modal').modal('show');
        }
    });
}

function confirm_new_spec(){
    //Approve generated yaml, save to GCP storage bucket
    var data = get_workout_form_data();

    $.ajax({
        type: "POST",
        url: "/admin/api/save_workout_spec", 
        data: JSON.stringify(data),
        contentType: "application/json;charset=utf-8"
    });
    
    var temp_file = new FormData();
    var teacher_file_element = $('#teacher_instruction_file:file');
    var teacher_instruction_file = teacher_file_element[0].files[0];
    var student_file_element = $('#student_instruction_file:file');
    var student_instruction_file = student_file_element[0].files[0];

    if(teacher_instruction_file){
        temp_file.append('teacher_instruction_file', teacher_instruction_file, teacher_instruction_file['name']);
    }
    if(student_instruction_file){
        temp_file.append('student_instruction_file', student_instruction_file, student_instruction_file['name']);
    }

    $.ajax({
        type:"POST",
        url: "/admin/api/upload_instructions", 
        data: temp_file,
        processData: false,
        contentType: false,
        success: function(response){
            console.log(response);
        }
    })
}

function get_instance_info(server_div_id){
    var server_div = document.getElementById(server_div_id);
    var instance_name = server_div.querySelector('.server_name').value;

    $.ajax({
        type: "POST",
        url: "/admin/api/instance_info",
        contentType: "application/json",
        data: JSON.stringify({"instance": instance_name}),
        success: function(data){
            var json = JSON.parse(data);
            if(json.nics){
                for(var i=0; i < json.nics.length; i++){
                    var new_nic = add_nic(server_div_id);
                    var ip_input = new_nic.querySelector('.nic_internal_ip');
                    ip_input.value = json.nics[i]['ip'];
                }
            }
        }
    })
}

function create_remove_button(div_id, div_type){
    var button = document.createElement("a");
    button.className = "btn remove_item_btn";
    button.innerHTML = "Remove " + div_type;
    button.href = "javascript:void(0)";
    button.style.marginTop = "1em";
    

    var dest_div = document.getElementById(div_id);
    $(button).on('click', function(){
        $(dest_div).remove();
    })
    dest_div.appendChild(button);
}

function add_tag(server_id){
    var server = document.getElementById(server_id);
    var tag_div = server.querySelector(".tag_div");
    var num_tags = tag_div.getElementsByClassName('tag_item').length;
    var new_tag_div = document.createElement('div');
    new_tag_div.className = "tag_item row";
    new_tag_div.id = server_id + "_tag_" + num_tags;
    var tag_input = document.createElement('input');
    tag_input.type = "text";
    tag_input.className = "server_tag form-control";
    tag_input.placeholder = "Tag";
    tag_input.style.width = "auto";
    new_tag_div.appendChild(tag_input);


    tag_div.appendChild(new_tag_div);
    create_remove_button(new_tag_div.id, "Tag");
}

function add_subnetwork(network){
    var network_div = document.getElementById(network);
    var subnet_div = network_div.getElementsByClassName('subnet_div')[0];//There is only one of these per network_div
    
    //Subnet Name
    var subnet_name = document.createElement('input');
    subnet_name.type = "text";
    subnet_name.placeholder = "Subnet Name";
    subnet_name.className = "subnet_name form-control";

    //Subnet IP
    var subnet_ip = document.createElement('input')
    subnet_ip.type = "text";
    subnet_ip.placeholder = "10.1.1.0/24";
    subnet_ip.name = "subnet_ip"
    subnet_ip.className = "subnet_ip form-control";

    //Group inputs into a subnet object container
    var subnet_input = document.createElement('div');
    subnet_input.className = "subnet_group form-group";
    subnet_input.style.border  
    subnet_input.appendChild(subnet_name);
    subnet_input.appendChild(subnet_ip);

    subnet_div.appendChild(subnet_input);
    
}
function new_network(){
    var network_container = document.getElementById('network_container');
    var network_count = network_container.childElementCount;
    //Create div for an individual network
    var network_div = document.createElement('div');
    network_div.id = "network_" + network_count;
    network_div.className = "network_info_container"
    //Network Name
    var network_name_input = document.createElement('input');
    network_name_input.type = "text"
    network_name_input.className = "network_name form-control"; 
    network_name_input.name = "network_name_" + network_count;
    network_name_input.placeholder = "Enter Network Name";
    network_div.appendChild(network_name_input);

    //Subnet Container
    var subnet_div = document.createElement('div');
    subnet_div.className = "subnet_div";
    var subnet_header = document.createElement('h3');
    subnet_header.innerHTML = "Subnets";
    subnet_div.appendChild(subnet_header)

    var add_subnet_button = document.createElement('a');
    add_subnet_button.className = "btn";
    add_subnet_button.style.width = "auto";
    add_subnet_button.style.margin = "auto";
    add_subnet_button.innerHTML = "Add Subnet";
    add_subnet_button.href = "javascript:void(0)"
    add_subnet_button.setAttribute('onclick', 'add_subnetwork("' + network_div.id + '")');
    subnet_div.appendChild(add_subnet_button);
    network_div.appendChild(subnet_div);
    

    network_container.appendChild(network_div);
    create_remove_button(network_div.id, "Network");
    return network_div;
}

function add_nic(server){
    //Add nic subelement to the server container
    var server_div = document.getElementById(server);
    var nic_div = server_div.getElementsByClassName('nic_div')[0];
    var nic_group = document.createElement('div');
    nic_group.className = "nic_group";
    nic_group.id = server_div.id + "_nic_" + (nic_div.getElementsByClassName('nic_group').length + 1);
    nic_div.appendChild(nic_group)

    var network_names = document.getElementsByClassName('network_name');
    var network_select = document.createElement('select');
    network_select.name="nic_" + server + "_network";
    network_select.id=network_select.name;
    network_select.className = "nic_network_select form-control";

    //Adds all available network names to select element on click
    $(network_select).on('focus', function(){
        while(network_select.firstChild){
            network_select.removeChild(network_select.firstChild);
        }
        for(var i = 0; i < network_names.length; i++){
            var option = document.createElement('option');
            option.value = network_names[i].value;
            option.innerHTML = network_names[i].value;
            network_select.appendChild(option);
            
        }
    })

    nic_group.appendChild(network_select);
    add_label(network_select.id, "Select a network (defined above)");

    var ip_input = document.createElement('input');
    ip_input.type = "text";
    ip_input.placeholder = "10.1.1.11";
    ip_input.className = "nic_internal_ip form-control";
    ip_input.name="nic_ip_" + server + (nic_div.getElementsByClassName('nic_group').length + 1);
    ip_input.id = ip_input.name;
    nic_group.appendChild(ip_input);
    add_label(ip_input.id, "Add an internal IP address")

    // server_div.appendChild(nic_div);

    create_remove_button(nic_group.id, "NIC");
    return nic_div;
}

function add_image_options(server_div, image_list){
    //Adds GCP VM image information to server select element
    //image_list is provided from Jinja template
    var select_element = server_div.querySelector(".server_name");
    while(select_element.firstChild){
        select_element.removeChild(select_element.firstChild);
    }
    if(select_element){
        for(var i = 0; i < image_list.length; i++){
            var image_option = document.createElement('option');
            image_option.value = image_list[i];
            image_option.innerHTML = image_list[i];
            select_element.appendChild(image_option);
        }
    }
}

function new_server(){
    //Create a new server group
    var server_container = document.getElementById('server_container');
    var server_count = server_container.childElementCount;

    var server_div = document.createElement('div');
    server_div.id = "server_" + server_count;
    server_div.className = "server_info_container";

    server_container.appendChild(server_div);

    //Server Instance template
    var server_image_input = document.createElement('select');
    server_image_input.className = "server_name form-control";
    server_image_input.name = "server_name_" + server_count;
    server_image_input.id = server_image_input.name;
    server_div.appendChild(server_image_input);
    add_label(server_image_input.id, "Select a GCP VM instance to duplicate");

    var get_instance_info_btn = document.createElement('a');
    get_instance_info_btn.className='btn instance_info_btn';
    get_instance_info_btn.innerHTML = "Get Machine Info";
    get_instance_info_btn.href = "javascript:void(0)";
    get_instance_info_btn.setAttribute("onclick", "get_instance_info('" + server_div.id + "')");
    server_div.appendChild(get_instance_info_btn);

    //Server tag list
    var tag_div = document.createElement('div');
    tag_div.className = "tag_div container";
    var tags_header = document.createElement('h3');
    tags_header.innerHTML = "Tags";
    tag_div.appendChild(tags_header);

    var add_tag_btn = document.createElement('a');
    add_tag_btn.className = "btn add_tag_btn";
    add_tag_btn.style.width = "auto";
    add_tag_btn.href = "javascript:void(0)";

    add_tag_btn.innerHTML = "Add Server Tag";
    add_tag_btn.setAttribute("onclick", "add_tag('" + server_div.id + "')");
    tag_div.appendChild(add_tag_btn);

    server_div.appendChild(tag_div);


    //Server NIC container
    var nic_div = document.createElement('div');
    nic_div.className = "nic_div container";
    var nics_header = document.createElement('h3');
    nics_header.innerHTML = "NICs";
    nic_div.appendChild(nics_header)

    var add_nic_button = document.createElement('a');
    add_nic_button.className = "btn";
    add_nic_button.style.width = "auto";
    add_nic_button.style.margin = "auto";
    add_nic_button.innerHTML = "Add NIC";
    add_nic_button.href = "javascript:void(0)";
    add_nic_button.setAttribute('onclick', 'add_nic("' + server_div.id + '")');
    nic_div.appendChild(add_nic_button);
    server_div.appendChild(nic_div);

    create_remove_button(server_div.id, "Server");

    return server_div;
}

function new_firewall(){
    //Add a firewall rule group
    var firewall_container = document.getElementById('firewall_container');
    var firewall_count = firewall_container.childElementCount;

    //Firewall Div
    var firewall_div = document.createElement('div');
    firewall_div.className = "firewall_info_container";
    firewall_div.id = "firewall_" + firewall_count;
    firewall_container.appendChild(firewall_div);

    //Firewall name input
    var firewall_name = document.createElement('input');
    firewall_name.className = "firewall_name form-control";
    firewall_name.name = "firewall_name_" + firewall_count;
    firewall_name.placeholder = "Firewall Name"
    firewall_div.appendChild(firewall_name);

    //Firewall network input
    var network_names = document.getElementsByClassName('network_name');
    var network_select = document.createElement('select');
    network_select.name="firewall_" + firewall_count + "_network";
    network_select.id = network_select.name;
    network_select.className = "firewall_network_select form-control"

    $(network_select).on('focus', function(){
        while(network_select.firstChild){
            network_select.removeChild(network_select.firstChild);
        }
        for(var i = 0; i < network_names.length; i++){
            var option = document.createElement('option');
            option.value = network_names[i].value;
            option.innerHTML = network_names[i].value;
            network_select.appendChild(option);
        }
    })
    firewall_div.appendChild(network_select);
    add_label(network_select.id, "Select a network (defined above)");

    //Firewall protocol
    var firewall_protocol = document.createElement('input');
    firewall_protocol.type = "text";
    firewall_protocol.name = "firewall_protocol_" + firewall_count;
    firewall_protocol.id = "firewall_protocol_" + firewall_count;
    firewall_protocol.placeholder = "tcp";
    firewall_protocol.className = "firewall_protocol form-control";

    firewall_div.appendChild(firewall_protocol);
    add_label(firewall_protocol.id, "Enter Firewall Protocol")

    //Firewall target tags
    var tag_select = document.createElement('select');
    tag_select.className = "firewall_tag_select form-control";
    tag_select.id = "firewall_tag_select_" + firewall_count;
    var tag_list = document.getElementsByClassName('server_tag');
    $(tag_select).on('focus', function(){
        while(tag_select.firstChild){
            tag_select.removeChild(tag_select.firstChild);
        }
        for(var i = 0; i < tag_list.length; i++){
            var option = document.createElement('option');
            option.value = tag_list[i].value;
            option.innerHTML = tag_list[i].value;
            tag_select.appendChild(option);
        }
    })
    
    firewall_div.appendChild(tag_select);
    add_label(tag_select.id, "Select firewall target tag");
    create_remove_button(firewall_div.id, "Firewall");

}

function new_assessment_question(){
    var assessment_container = document.getElementById('assessment_container');
    var question_count = assessment_container.childElementCount;
    
    //Assessment Question Div
    var assessment_div = document.createElement('div');
    assessment_div.className = "assessment_item";
    assessment_div.id = "assessment_question_" + question_count;
    assessment_container.appendChild(assessment_div);

    //Question Type
    var question_type = document.createElement('select');
    question_type.name = "question_" + question_count + "_type"
    question_type.className = "question_type form-control";
    assessment_div.appendChild(question_type);

    var type_list = ["input", "upload"];
    for(var i = 0; i < type_list.length; i++){
        var temp_option = document.createElement('option');
        temp_option.value = type_list[i];
        temp_option.innerHTML = type_list[i];
        question_type.appendChild(temp_option);
    }

    var question_text = document.createElement('input');
    question_text.className = "question_text form-control";
    question_text.type = "text";
    question_text.name = "question_" + question_count + "_text";
    question_text.id = question_text.name;
    assessment_div.appendChild(question_text);
    add_label(question_text.id, "Enter the question")

    var answer = document.createElement('input');
    answer.className = "answer form-control";
    answer.type = "text";
    answer.name = "question_" + question_count + "_answer";
    answer.id = answer.name;
    assessment_div.appendChild(answer);
    add_label(answer.id, "Enter the answer");

    create_remove_button(assessment_div.id, "Question")
}

function add_label(input, label_text){
    //Adds a label to form input element
    var input_element = document.getElementById(input);
    var templabel = document.createElement('label');
    templabel.for = input;
    templabel.innerHTML = label_text;

    input_element.parentNode.appendChild(templabel);
}


//Fill select fields with appropriate values
$('.nic_network_select').on('click', function(){
    var network_names = document.getElementsByClassName('network_name');
    for(var i = 0; i < network_names.length; i++){
        var option = document.createElement('option');
        option.value = network_names[i].value;
        option.innerHTML = network_names[i].value;
        network_select.appendChild(option);
    }
})

$("#host_ip_select").on('focus', function(){
    var ip_select = this;
    var ip_list = document.getElementsByClassName('nic_internal_ip');
    while(ip_select.firstChild){
        ip_select.removeChild(ip_select.firstChild);
    }
    for(var i = 0; i < ip_list.length; i++){
        var option = document.createElement('option');
        option.value = ip_list[i].value;
        option.innerHTML = ip_list[i].value;
        ip_select.appendChild(option);
    }
})

$("#student_entry_select").on('focus', function(){
    var network_names = document.getElementsByClassName('network_name');
    var network_select = this;
    while(network_select.firstChild){
        network_select.removeChild(network_select.firstChild);
    }
    for(var i = 0; i < network_names.length; i++){
        var option = document.createElement('option');
        option.value = network_names[i].value;
        option.innerHTML = network_names[i].value;
        network_select.appendChild(option);
    }
})
