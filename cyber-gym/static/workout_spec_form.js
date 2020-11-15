function get_workout_form_data(){
    var data = {};
    data['workout'] = [];

    //Get basic workout info
    var workout_info = {};
    workout_info['name'] = document.getElementById('workout_name').value;
    var build_type = document.getElementById('build_type_select').value;
    workout_info['build_type'] = build_type;
    workout_info['workout_description'] = document.getElementById('workout_description').value;

    //console.log(file_inputs);

    data['workout'] = workout_info;
    
    if(build_type == "compute"){
        //Process Networks
        var networks = document.getElementsByClassName('network_info_container');
        //var networks = document.getElementById('network_container');
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
            
            //alert(network_name.value);
        }

        //Process Servers
        var servers = document.getElementsByClassName('server_info_container');

        for(var i = 0; i < servers.length; i++){
            var server_info = {};
            var server_div = servers[i];

            var server_name = server_div.querySelector('.server_name');
            server_info['name'] = server_name.value;

            var server_image = server_div.querySelector('.server_image');
            server_info['image'] = server_image.value;

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
            if(!data['servers']){
                data['servers'] = [];
            }
            data['servers'][i] = server_info;
        }
        

        //Process Firewalls
        var firewalls = document.getElementsByClassName('firewall_info_container');

        for(var i = 0; i < firewalls.length; i++){
            var firewall_info = {};
            var firewall_div = firewalls[i];

            var firewall_name = firewall_div.querySelector('.firewall_name');
            firewall_info['name'] = firewall_name.value;

            var firewall_protocol = firewall_div.querySelector('.firewall_protocol')
            firewall_info['protocol'] = firewall_protocol.value;

            var firewall_network = firewall_div.querySelector('.firewall_network_select')
            firewall_info['network'] = firewall_network.value;
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
    var data = get_workout_form_data();
    $.ajax({
        type:"POST",
        url: "/create_workout_spec",
        data: JSON.stringify(data),
        contentType: "application/json;charset=utf-8",
        success: function(response){
            
            var lines = [];
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
    var data = get_workout_form_data();

    $.ajax({
        type: "POST",
        url: "/save_workout_spec", 
        data: JSON.stringify(data),
        contentType: "application/json;charset=utf-8"
    });
    
    var temp_file = new FormData();
    var teacher_file_element = $('#teacher_instruction_file:file');
    var teacher_instruction_file = teacher_file_element[0].files[0];
    var student_file_element = $('#student_instruction_file:file');
    var student_instruction_file = student_file_element[0].files[0];

    temp_file.append('teacher_instruction_file', teacher_instruction_file, teacher_instruction_file['name']);
    temp_file.append('student_instruction_file', student_instruction_file, student_instruction_file['name']);

    $.ajax({
        type:"POST",
        url: "/upload_instructions", 
        data: temp_file,
        processData: false,
        contentType: false,
        success: function(response){
            console.log(response);
        }
    })
}

function add_subnetwork(network){
    var network_div = document.getElementById(network);
    var subnet_div = network_div.getElementsByClassName('subnet_div')[0];//There is only one of these per network_div
    
    //Subnet Name
    var subnet_name = document.createElement('input');
    subnet_name.type = "text";
    subnet_name.placeholder = "Subnet Name";
    subnet_name.className = "subnet_name";

    //Subnet IP
    var subnet_ip = document.createElement('input')
    subnet_ip.type = "text";
    subnet_ip.placeholder = "10.1.1.0/24";
    subnet_ip.name = "subnet_ip"
    subnet_ip.className = "subnet_ip";

    //Group inputs into a subnet object container
    var subnet_input = document.createElement('div');
    subnet_input.className = "subnet_group";
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
    network_name_input.className = "network_name"
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
    add_subnet_button.setAttribute('onclick', 'add_subnetwork("' + network_div.id + '")');
    subnet_div.appendChild(add_subnet_button);
    network_div.appendChild(subnet_div);
    

    network_container.appendChild(network_div);
    return network_div;
}

function add_nic(server){
    var server_div = document.getElementById(server);
    var nic_div = server_div.getElementsByClassName('nic_div')[0];

    var network_names = document.getElementsByClassName('network_name');
    var network_select = document.createElement('select');
    network_select.name="nic_" + server + "_network";
    network_select.className = "nic_network_select"
    for(var i = 0; i < network_names.length; i++){
        var option = document.createElement('option');
        option.value = network_names[i].value;
        option.innerHTML = network_names[i].value;
        network_select.appendChild(option);
        //network_select.appendChild(document.createElement('option').value=network_names[i]);
    }

    var ip_input = document.createElement('input');
    ip_input.type = "text";
    ip_input.placeholder = "10.1.1.11";
    ip_input.className = "nic_internal_ip";
    ip_input.name="nic_ip";
    var nic_group = document.createElement('div');
    nic_group.className = "nic_group";
    nic_group.appendChild(ip_input);
    nic_group.appendChild(network_select)
    nic_div.appendChild(nic_group)


    server_div.appendChild(nic_div);
}

function new_server(){
    var server_container = document.getElementById('server_container');
    var server_count = server_container.childElementCount;

    var server_div = document.createElement('div');
    server_div.id = "server_" + server_count;
    server_div.className = "server_info_container";

    //Server Name
    var server_name_input = document.createElement('input');
    server_name_input.type = "text";
    server_name_input.className = "server_name";
    server_name_input.name = "server_name_" + server_count;
    server_name_input.placeholder = "Enter Server Name";
    server_div.appendChild(server_name_input);

    //Server Image
    var server_image_input = document.createElement('input');
    server_image_input.type = "text";
    server_image_input.className = "server_image";
    server_image_input.name = "server_image_" + server_count;
    server_image_input.placeholder = "Enter Server Image Name";
    server_div.appendChild(server_image_input);

    //Server NIC container
    var nic_div = document.createElement('div');
    nic_div.className = "nic_div";
    var nics_header = document.createElement('h3');
    nics_header.innerHTML = "NICs";
    nic_div.appendChild(nics_header)

    var add_nic_button = document.createElement('a');
    add_nic_button.className = "btn";
    add_nic_button.style.width = "auto";
    add_nic_button.style.margin = "auto";
    add_nic_button.innerHTML = "Add NIC";
    add_nic_button.setAttribute('onclick', 'add_nic("' + server_div.id + '")');
    nic_div.appendChild(add_nic_button);
    server_div.appendChild(nic_div);

    server_container.appendChild(server_div);
    return server_div;
}

function new_firewall(){
    var firewall_container = document.getElementById('firewall_container');
    var firewall_count = firewall_container.childElementCount;

    //Firewall Div
    var firewall_div = document.createElement('div');
    firewall_div.className = "firewall_info_container";
    firewall_div.id = "firewall_" + firewall_count;
    firewall_container.appendChild(firewall_div);

    //Firewall name input
    var firewall_name = document.createElement('input');
    firewall_name.className = "firewall_name";
    firewall_name.name = "firewall_name_" + firewall_count;
    firewall_name.placeholder = "Firewall Name"
    firewall_div.appendChild(firewall_name);

    //Firewall network input
    var network_names = document.getElementsByClassName('network_name');
    var network_select = document.createElement('select');
    network_select.name="firewall_" + firewall_count + "_network";
    network_select.className = "firewall_network_select"
    for(var i = 0; i < network_names.length; i++){
        var option = document.createElement('option');
        option.value = network_names[i].value;
        option.innerHTML = network_names[i].value;
        network_select.appendChild(option);
    }
    firewall_div.appendChild(network_select);

    //Firewall protocol
    var firewall_protocol = document.createElement('input');
    firewall_protocol.type = "text";
    firewall_protocol.name = "firewall_protocol_" + firewall_count;
    firewall_protocol.id = "firewall_protocol_" + firewall_count;
    firewall_protocol.placeholder = "tcp";
    firewall_protocol.className = "firewall_protocol";

    firewall_div.appendChild(firewall_protocol);
    add_label(firewall_protocol.id, "Enter Firewall Protocol")


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
    question_type.className = "question_type";
    assessment_div.appendChild(question_type);

    var type_list = ["input", "upload"];
    for(var i = 0; i < type_list.length; i++){
        var temp_option = document.createElement('option');
        temp_option.value = type_list[i];
        temp_option.innerHTML = type_list[i];
        question_type.appendChild(temp_option);
    }

    var question_text = document.createElement('input');
    question_text.className = "question_text";
    question_text.type = "text";
    question_text.name = "question_" + question_count + "_text";
    question_text.id = question_text.name;
    assessment_div.appendChild(question_text);
    add_label(question_text.id, "Enter the question")

    var answer = document.createElement('input');
    answer.className = "answer";
    answer.type = "text";
    answer.name = "question_" + question_count + "_answer";
    answer.id = answer.name;
    assessment_div.appendChild(answer);
    add_label(answer.id, "Enter the answer");
}

function add_label(input, label_text){
    var input_element = document.getElementById(input);
    var templabel = document.createElement('label');
    templabel.for = input;
    templabel.innerHTML = label_text;

    input_element.parentNode.appendChild(templabel);
}

function format_runtime(){
    var runtime_list = document.getElementsByClassName('runtime_field');
    for(var i = 0; i < runtime_list.length; i++){
        var runtime_s = runtime_list[i].innerHTML;
        var minutes = Math.floor((runtime_s / 60))
        var seconds = runtime_s % 60
        var formatted_runtime = minutes.toString() + "min " + seconds.toString() + "sec";
        runtime_list[i].innerHTML = formatted_runtime;
    }
}
