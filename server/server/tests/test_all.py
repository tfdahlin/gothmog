from contextlib import contextmanager
from multiprocessing import Event, Process
from unittest import TestCase
from wsgiref.simple_server import make_server
import os, sys

import requests

from main import app
from util import BaseHandler

test_port = '9001'
test_address = '127.0.0.1'
test_protocol = 'http'
test_url = f'{test_protocol}://{test_address}:{test_port}'

@contextmanager
def captured_output():
    new_out, new_err = io.StringIO(), io.StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err

class MyServer:
    def __init__(self):
        self.e = Event()
        self.server = Process(target=self._run, name='Server_Process')
        self.e.set()
    
    def start(self):
        print(f"Starting server on port {test_port}... ", end='')
        self.server.start()
        print(f"Done.")

    def stop(self):
        print("Stopping server...")
        self.e.clear()
        try:
            requests.get(test_url)
        except Exception as e:
            print("Exception while attempting to handle stop request:")
            raise e
        self.server.join()
        print("Server stopped.")
        self.server = Process(target=self._run, name='Server_Process')
        self.e.set()

    def _run(self):
        old_out, old_err = sys.stdout, sys.stderr
        sys.stdout = open(os.devnull, 'w')
        sys.stderr = open(os.devnull, 'w')

        try:
            httpd = make_server('127.0.0.1', 9001, app)
            not_running = False
        except ConnectionError:
            print(f'Port 9001 already in use.')
            return
        while self.e.is_set():
            httpd.handle_request()
        httpd.server_close()
        sys.stdout, sys.stderr = old_out, old_err

class create_server:
    def __enter__(self):
        self.s = MyServer()
        self.s.start()
        return self.s

    def __exit__(self, type, value, traceback):
        self.s.stop()

class TestServer(TestCase):
    def make_op(self):
        """Create an op object in the database using the API."""
        r = requests.post(f'{test_url}/op/create', json={'op_name':'test'})
        return r

    def delete_op(self):
        """Delete an op object from the database using the API."""
        r = requests.post(f'{test_url}/op/delete', json={'op_name': 'test'})
        return r

    def upload_file(self):
        """Upload a file using the API."""
        r = requests.put(f'{test_url}/files/upload', data={'op_name':'test'}, files={'file': ('test_file.txt', 'asdf', 'text/plain')})
        return r

    def delete_file(self, guid):
        """Delete a file using the API."""
        r = requests.post(f'{test_url}/files/delete', json={'file': guid})
        return r

    def post_shell_cmd(self):
        """Post a shell command to the database using the API."""
        test_cmd = {
            'op_name': 'test',
            'cmd_type': 'shell',
            'cmd_data': """echo 'Hello world!'""",
        }
        
        r = requests.post(f'{test_url}/post', json=test_cmd)
        return r

    def test_ping(self):
        """Test the /ping URI."""
        r = requests.get(f'{test_url}/ping')
        assert r.json()['data']['msg'] == 'Pong!', "Ping failed."

    def test_home(self):
        """Test the / URI."""
        r = requests.get(f'{test_url}/')
        assert r.status_code == 200, 'Did not get 200 response.'

    def test_post(self):
        """Test posting a new command."""
        self.make_op()
        r = self.post_shell_cmd()
        assert r.status_code == 200, 'Did not successfully make new command.'
        self.delete_op()

    def test_upload(self):
        """Test uploading a file."""
        self.make_op()
        r = self.upload_file()
        assert r.status_code == 200, 'Did not successfully upload file.'
        self.delete_op()

    def test_make_op(self):
        """Test creating an op."""
        r = self.make_op()
        assert r.status_code == 200, 'Did not successfully create op.'
        self.delete_op()

    def test_delete_op(self):
        """Test deleting an op."""
        self.make_op()
        # Delete the op
        r = self.delete_op()
        assert r.status_code == 200, 'Bad response while deleting op.'

        r = requests.get(f'{test_url}/op/test')
        assert r.status_code == 404, 'Did not successfully delete op.'

        r = requests.get(f'{test_url}/op')
        print(r.json())
        assert 'test' not in r.json()['data']['ops'], 'Did not successfully delete op.'

    def test_get_files(self):
        """Fetch the file list."""
        # TODO: upload multiple files, and make sure they're all listed
        f1 = self.upload_file().json()['data']['guid']
        f2 = self.upload_file().json()['data']['guid']
        r = requests.get(f'{test_url}/files')
        assert f1 in r.json()['data']['files']
        assert f2 in r.json()['data']['files']

    def test_delete_file(self):
        """Delete a file."""
        f1 = self.upload_file().json()['data']['guid']
        r = self.delete_file(f1)
        assert r.status_code == 200, 'Server did not return success when deleting file.'
        r = requests.get(f'{test_url}/files/download/{f1}')
        print(r)
        print(r.content)
        assert r.status_code == 404, 'File not deleted.'
        r = requests.get(f'{test_url}/files')
        assert f1 not in r.json()['data']['files'], 'File not deleted.'
