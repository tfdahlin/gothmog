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

class MyServer:
    def __init__(self):
        self.e = Event()
        self.server = Process(target=self._run, name='Server_Process')
        self.e.set()
    
    def start(self):
        self.server.start()

    def stop(self):
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
        httpd = make_server('127.0.0.1', 9001, app)
        not_running = False
        while self.e.is_set():
            httpd.handle_request()
        httpd.server_close()

def setup_package():
    global http_server
    http_server = MyServer()
    http_server.start()

def teardown_package():
    global http_server
    http_server.stop()
