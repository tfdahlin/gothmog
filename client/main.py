#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename: main.py

# Native python imports
import sys

# PIP library imports

# Local file imports
from client.client import Client

def usage():
    """Print usage information for the script."""
    if len(sys.argv) < 2:
        print(f'Usage: {sys.argv[0]} <server_address> <op_name> [options]')
        print()
        exit()

def main(server_address, op_name):
    """Main takes two arguments, so that it can be run by import.
    These arguments are passed from the command line when run standalone.
    """
    c = Client(server_address, op_name)
    c.start()

if __name__ == "__main__":
    usage()
    main(sys.argv[1], sys.argv[2])
