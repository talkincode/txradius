#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import random
from txradius.radius import dictionary
from txradius import client
import ConfigParser

CONFIG_FILE = '/etc/openvpn/txovpn.conf'
DICTIONARY_FILE = os.path.join(os.path.dirname(client.__file__), "dictionary/ovpn_dictionary")

ACCT_START = 1
ACCT_STOP = 2
ACCT_UPDATE = 3

get_dictionary = lambda: dictionary.Dictionary(DICTIONARY_FILE)

get_challenge = lambda : ''.join(chr(b) for b in [random.SystemRandom().randrange(0, 256) for i in range(16)])

def readconfig(cfgfile):
    config = ConfigParser.RawConfigParser()
    config.read(cfgfile)
    return config