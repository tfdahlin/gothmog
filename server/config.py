import os

API_VERSION='1.0.0'
class HostDict:
    def __init__(self):
        self.all_items = [
            # allowed addresses here!
            '127.0.0.1'
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
        r10 = True
        r192 = True
        r172 = True
        try:
            if item in self.all_items:
                return True

            if r192: # allow 192.168.0.0/16 range
            #if False: # disallow 192.168.0.0/16 range
                a, b, _, _ = item.split('.')
                if a == '192' and b == '168':
                    return True

            if r10: # allow 10.0.0.0/8 range
            #if False: # disallow 10.0.0.0/8 range
                a, _, _, _ = item.split('.')
                if a == '10':
                    return True

            # 172.16.0.0 - 172.31.255.255
            if r172: # allow 172.16.0.0/12 range
            #if False: # disallow 172.16.0.0/12 range
                a, b, _, _ = item.split('.')
                if a == '172' and (16 <= int(b) <= 31):
                    return True
        except Exception as e:
            print("Exception encountered while attempting to parse ip.")
            print(e)
            return False
        else:
            return False
        
allowed_hosts = HostDict()
