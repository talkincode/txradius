#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys,os
from twisted.python.logfile import DailyLogFile
from twisted.internet.protocol import Protocol, Factory
from txradius import message, client
from txradius.radius import dictionary,packet
from twisted.internet import reactor, defer
from twisted.python import log
import json
import functools
import random
import time
import ConfigParser
import traceback
import click

CONFIG_FILE = '/etc/openvpn/txovpn.conf'

ACCT_START = 1
ACCT_STOP = 2
ACCT_UPDATE = 3

get_dictionary = lambda: dictionary.Dictionary(os.path.join(os.path.dirname(client.__file__), "dictionary/ovpn_dictionary"))

get_challenge = lambda : ''.join(chr(b) for b in [random.SystemRandom().randrange(0, 256) for i in range(16)])

def readconfig(cfgfile):
    config = ConfigParser.RawConfigParser()
    config.read(cfgfile)
    return config

@click.group()
def cli():
    pass

@click.command()
@click.option('-c','--conf', default=CONFIG_FILE, help='txovpn config file')
@click.option('-d','--debug', is_flag=True)
def user_pass_verify(conf,debug):
    """ OpenVPN user_pass_verify method
    """
    config = readconfig(conf)
    log.startLogging(DailyLogFile.fromFullPath(config.get("DEFAULT",'logfile')))
    nas_id = config.get('DEFAULT', 'nas_id')
    secret = config.get('DEFAULT', 'secret')
    nas_addr = config.get('DEFAULT', 'nas_addr')
    radius_addr = config.get('DEFAULT', 'radius_addr')
    radius_auth_port = config.get('DEFAULT', 'radius_auth_port')
    req = {'User-Name':os.environ.get('username')}
    req['CHAP-Challenge'] = get_challenge()
    req['CHAP-Password-Plaintext'] = os.environ.get('password')
    req["NAS-IP-Address"]     = nas_addr
    req["NAS-Port-Id"]     = '0/0/0:0.0'
    req["NAS-Port"]           = 0
    req["Service-Type"]       = "Login-User"
    req["NAS-Identifier"]     = nas_id
    req["Called-Station-Id"]  = '00:00:00:00:00:00'
    req["Calling-Station-Id"] = '00:00:00:00:00:00'
    req["Framed-IP-Address"]  = os.environ.get('ifconfig_pool_remote_ip')
    log.msg("radius auth: %s" % repr(req))

    def onresp(r):
        log.msg(message.format_packet_str(r))
        reactor.stop()
        sys.exit(0)

    def onerr(e):
        log.err(e)
        reactor.stop()
        sys.exit(1)

    d = client.send_auth(str(secret), get_dictionary(), radius_addr, 
        authport=radius_auth_port, debug=True,**req)
    d.addCallbacks(onresp,onerr)
    reactor.run()    


@click.command()
@click.option('-c','--conf', default=CONFIG_FILE, help='txovpn config file')
@click.option('-d','--debug', is_flag=True)
def client_connect(conf,debug):
    """ OpenVPN client_connect method
    """
    config = readconfig(conf)
    log.startLogging(DailyLogFile.fromFullPath(config.get("DEFAULT",'logfile')))
    nas_id = config.get('DEFAULT', 'nas_id')
    secret = config.get('DEFAULT', 'secret')
    nas_addr = config.get('DEFAULT', 'nas_addr')
    radius_addr = config.get('DEFAULT', 'radius_addr')
    radius_acct_port = config.get('DEFAULT', 'radius_acct_port')
    session_id = 0
    req = {'User-Name':os.environ.get('username')}
    req['Acct-Status-Type'] = ACCT_STOP
    req['Acct-Session-Id'] = session_id
    req["Acct-Output-Octets"]  =  0
    req["Acct-Input-Octets"]  =  0 
    req['Acct-Session-Time'] = 0
    req["NAS-IP-Address"]     = nas_addr
    req["NAS-Port-Id"]     = '0/0/0:0.0'
    req["NAS-Port"]           = 0
    req["Service-Type"]       = "Login-User"
    req["NAS-Identifier"]     = nas_id
    req["Called-Station-Id"]  = '00:00:00:00:00:00'
    req["Calling-Station-Id"] = '00:00:00:00:00:00'
    req["Framed-IP-Address"]  = os.environ.get('ifconfig_pool_remote_ip')
    log.msg("radius acct: %s" % repr(req))

    def onresp(r):
        log.msg(message.format_packet_str(r))
        reactor.stop()
        sys.exit(0)

    def onerr(e):
        log.err(e)
        reactor.stop()
        sys.exit(1)

    d = client.send_acct(str(secret), get_dictionary(), radius_addr, 
        acctport=radius_acct_port, debug=True,**req)
    d.addCallbacks(onresp,onerr)
    reactor.run()    



cli.add_command(user_pass_verify)
cli.add_command(client_connect)
cli.add_command(client_disconnect)


if __name__ == '__main__':
    cli()
