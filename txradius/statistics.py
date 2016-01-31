#!/usr/bin/env python
# coding=utf-8
import time
from collections import deque

class MessageStat(dict):

    def __init__(self):
        self.online = 0
        self.auth_all = 0
        self.auth_all_old = 0
        self.auth_accept = 0
        self.auth_reject = 0
        self.auth_drop = 0
        self.acct_all = 0
        self.acct_all_old = 0
        self.acct_start = 0
        self.acct_stop = 0
        self.acct_update = 0
        self.acct_on = 0
        self.acct_off = 0
        self.acct_retry = 0
        self.acct_drop = 0
        self.auth_stat = deque([],60)
        self.acct_stat = deque([],60)

    def incr(self, attr_name, incr=1):
        if hasattr(self, attr_name):
            setattr(self, attr_name, getattr(self,attr_name) + incr)
        
    def run_stat(self):
        _time = time.time()*1000
        _auth_msg = self.auth_all - self.auth_all_old
        self.auth_all_old = self.auth_all
        _acct_msg = self.acct_all - self.acct_all_old
        self.acct_all_old = self.acct_all
        self.auth_stat.append((_time,_auth_msg))
        self.acct_stat.append((_time,_acct_msg))

    def __getattr__(self, key): 
        try:
            return self[key]
        except KeyError, k:
            raise AttributeError, k
    
    def __setattr__(self, key, value): 
        self[key] = value
    
    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError, k:
            raise AttributeError, k        
