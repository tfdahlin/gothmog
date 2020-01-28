#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename: server/config.py

# Native python imports
import logging, os

# PIP library imports
from netaddr import *

# Local file imports

log_file = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'app.log'
)

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s - %(message)s',
                    level=logging.INFO, filename=log_file)

API_VERSION='1.0.0'

class HostDict:
    """Class used to determine what hosts are allowed to access specific resources.

    This mostly serves as a wrapper class to allow membership tests elsewhere in the code,
    e.g. if incoming_ip_address in allowed_ip_addresses.

    Attributes:
        all_items (list): List of allowed host subnets (X.X.X.X/X format).
    """
    def __init__(self):
        self.all_items = [
            # allowed addresses here!
            '127.0.0.0/8',
            '10.0.0.0/8',
            '172.16.0.0/12',
            '192.168.0.0/16',
        ]
        self.load_allowed_addresses()

    def load_allowed_addresses(self):
        """Load the list of additional allowed subnets from allowed_addresses.txt"""
        curr_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(curr_dir, 'allowed_addresses.txt')
        all_addrs = None
        try:
            with open(file_path) as f:
                all_addrs = f.readlines()
                for addr in all_addrs:
                    self.all_items.append(addr)
        except FileNotFoundError as e:
            logger.info(f'No allowed_addresses.txt file found. Using default local addresses only.')
            return

    def __contains__(self, item):
        """Magic method override to allow for 'X in Y' membership checks."""
        try:
            for subnet in self.all_items:
                if item in IPNetwork(subnet):
                    return True
        except Exception as e:
            logger.warning("Exception encountered while attempting to parse ip.")
            logger.warning(e)
            return False
        else:
            return False
        
allowed_hosts = HostDict()
