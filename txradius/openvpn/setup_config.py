#!/usr/bin/env python
# -*- coding: utf-8 -*-

confstr = '''[DEFAULT]
nas_id=txovpn
nas_coa_port=3799
nas_addr=127.0.0.1
radius_addr=127.0.0.1
radius_auth_port=18121
radius_acct_port=18131
radius_secret=secret
radius_timeout=3
acct_interval=60
session_timeout=864000
logfile=/var/log/txovpn.log
statusfile=/etc/openvpn/openvpn-status.log
statusdb=/etc/openvpn/txovpn.db
client_config_dir=/etc/openvpn/ccd
server_manage_addr=127.0.0.1:7505
'''

def echo():
    print confstr

if __name__ == '__main__':
    print confstr
