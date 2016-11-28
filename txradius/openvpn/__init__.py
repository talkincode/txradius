#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import random
import time
import ConfigParser
from decimal import Decimal
from txradius import client
from txradius.radius import dictionary
from twisted.python import log
from twisted.python.logfile import DailyLogFile

CONFIG_FILE = '/etc/openvpn/txovpn.conf'
DICTIONARY_FILE = os.path.join(os.path.dirname(client.__file__), "dictionary/ovpn_dictionary")

ACCT_START = 1
ACCT_STOP = 2
ACCT_UPDATE = 3

get_dictionary = lambda : dictionary.Dictionary(DICTIONARY_FILE)

get_challenge = lambda : ''.join(chr(b) for b in [random.SystemRandom().randrange(0, 256) for i in range(16)])

__defconfig__ = dict(
    nas_id='txovpn',
    nas_coa_port='3799',
    nas_addr='127.0.0.1',
    radius_addr='127.0.0.1',
    radius_auth_port='1812',
    radius_acct_port='1813',
    radius_secret='secret',
    radius_timeout='3',
    acct_interval='60',
    session_timeout='864000',
    logfile='/var/log/txovpn.log',
    statusfile='/etc/openvpn/openvpn-status.log',
    statusdb='/etc/openvpn/txovpn.db',
    client_config_dir="/etc/openvpn/ccd",
    server_manage_addr="127.0.0.1:7505",
    debug="true",
)

def init_config(cfgfile):
    config = ConfigParser.SafeConfigParser(__defconfig__)
    config.read(cfgfile)
    if config.getboolean('DEFAULT', 'debug'):
        log.startLogging(sys.stdout)
    else:
        log.startLogging(DailyLogFile.fromFullPath(config.get("DEFAULT",'logfile')))    
    return config



