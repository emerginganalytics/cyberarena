#!/usr/bin/python3
from psutil import disk_usage, virtual_memory
from requests import get


class SystemInfo(object):
    def __init__(self, **kwargs):
        self.mem = self.get_mem
        self.ext_ip = self.get_ip
        self.storage = self.get_storage

    @property
    def get_mem(self):
        self._mem = virtual_memory()[2]
        return f'{self._mem}'

    @property
    def get_ip(self):
        self._ext_ip = get('https://api.ipify.org').text
        return self._ext_ip 

    @property
    def get_storage(self):
        self._storage = disk_usage('/').percent
        return f'{self._storage}'
    
    def get_all_info(self):
        return {'memory': self.mem, 'ip': self.ext_ip, 'storage': self.storage}
