import os

from netaddr import *

API_VERSION='1.0.0'
class HostDict:
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
        # Load ./allowed_addresses.txt for additional addresses
        curr_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(curr_dir, 'allowed_addresses.txt')
        all_addrs = None
        try:
            with open(file_path) as f:
                all_addrs = f.readlines()
        except FileNotFoundError as e:
            return

        # Add all the addresses in allowed_addresses.txt to
        #  the list of allowed addresses.
        if all_addrs:
            for addr in all_addrs:
                self.all_items.append(addr)
        
    def __contains__(self, item):
        try:
            for subnet in self.all_items:
                if item in IPNetwork(subnet):
                    return True
        except Exception as e:
            print("Exception encountered while attempting to parse ip.")
            print(e)
            return False
        else:
            return False
        
allowed_hosts = HostDict()
