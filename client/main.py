import sys, time, os, threading, datetime

import requests

default_wait_time = 5
retry_wait_time = 60
extended_wait_time = 3600
retry_threshold = 10

def usage():
    if len(sys.argv) < 2:
        print(f'Usage: {sys.argv[0]} server_address op_name')
        exit()

class Client:
    def __init__(self, server_addr: str, op_name: str):
        self.retries = 0
        self.prev = None
        self.server_addr = server_addr
        self.op_name = op_name

    def update_cache_file(self):
        curr_folder = os.path.dirname(os.path.abspath(__file__))
        cached_cmd_file = os.path.join(curr_folder, 'prev_cmd.txt')
        if self.prev:
            with open(cached_cmd_file, 'w') as f:
                f.write(self.prev)

    def handle_timeout(self):
        self.retries += 1
        if self.retries % retry_threshold == 0:
            print(f"Max retries exceeded. Retrying in {extended_wait_time} seconds.")
            return extended_wait_time
        print(f'Exception retrieving command. Retrying in {retry_wait_time} seconds.')
        return retry_wait_time

    def fetch_next_command(self) -> int:
        if self.prev:
            try:
                r = requests.get(f'{self.server_addr}/cmd/{self.prev}')
                if r.status_code != 200:
                    self.retries = 0
                    return default_wait_time
                
                data = r.json()['data']

                # Proceed if there's a new command, otherwise
                #  wait before trying again.
                if 'next' in data:
                    return self.fetch_command(data['next'])
                else:
                    self.retries = 0
                    return default_wait_time
            except Exception as e:
                print(e)
                return self.handle_timeout()
        else:
            return self.fetch_latest_command()
    
    def fetch_latest_command(self) -> int:
        try:
            r = requests.get(f'{self.server_addr}/op/fetch/{self.op_name}')
            if r.status_code != 200:
                return default_wait_time
            cmd_id = r.json()['data']['guid']
            return self.fetch_command(cmd_id)
        except Exception as e:
            print(e)
            return self.handle_timeout()
        else:
            self.retries = 0
            return retry_wait_time

    def fetch_command(self, cmd_id):
        try:
            r = requests.get(f'{self.server_addr}/cmd/{cmd_id}')
            data = r.json()['data']
        except Exception as e:
            print(e)
            return self.handle_timeout()
        else:
            self.prev = cmd_id
            self.update_cache_file()
            self.handle_command(data)

            self.retries = 0
            if 'next' in data:
                return self.fetch_command(data['next'])
            else:
                return default_wait_time

    def handle_command(self, data):
        if 'type' not in data:
            return
        if data['type'] == 'shell':
            print(f"Executing shell command: {data['cmd']}")
            ret_val = os.system(data['cmd'])
        if data['type'] == 'python':
            program = data['cmd']
            t = threading.Thread(target=exec, args=[program])
            t.start()
        if data['type'] == 'control':
            if data['cmd'] == 'stop':
                exit()
        # TODO: additional command types?
            
def main():
    print(f'Program starting at {datetime.datetime.now()}\n')
    c = Client(sys.argv[1])
    curr_folder = os.path.dirname(os.path.abspath(__file__))
    cached_cmd_file = os.path.join(curr_folder, 'prev_cmd.txt')
    if os.path.exists(cached_cmd_file):
        with open(cached_cmd_file, 'r') as f:
            last_cmd = f.read().strip()
            c.prev = last_cmd
    while True:
        sleep_time = c.fetch_next_command()
        if sleep_time:
            time.sleep(sleep_time)

if __name__ == "__main__":
    usage()
    main()
