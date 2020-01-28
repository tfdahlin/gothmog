#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename: client/tests/__init__.py

# Native python imports
import os, logging, socket

# PIP library imports

# Local file imports


curr_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)))
server_dir = os.path.abspath(os.path.join(curr_dir, os.pardir, os.pardir, 'server'))
print(server_dir)
nose_logfile = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'nose_log.txt')
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, filename=nose_logfile)

def port_in_use(port):
    """Determine whether or not a given port is already in use.

    Arguments:
        port (int): The port to check the availability of.

    Returns:
        result (bool): Whether or not the port is in use.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def setup_package():
    """Initial setup for testing package.

    This creates a temporary local gothmog server to run client tests against.
    """
    server_port = 13889
    if port_in_use(server_port):
        raise socket.error('Port 13889 in use.')
    print(f'Test port: {server_port}')
    

    # Start a local server on a likely unused port
    # We're arbitrarily choosing 13889
    
    pass

def teardown_package():
    pass
