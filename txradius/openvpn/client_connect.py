#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys,os
from twisted.python import log
from twisted.internet import reactor, defer
from txradius.radius import dictionary,packet,tools
from txradius.openvpn import CONFIG_FILE,ACCT_START
from txradius.openvpn import get_challenge
from txradius.openvpn import get_dictionary
from txradius.openvpn import init_config
from txradius.openvpn import statusdb
from txradius import message, client
from hashlib import md5
import traceback
import click
import time

@click.command()
@click.option('-c','--conf', default=CONFIG_FILE, help='txovpn config file')
def cli(conf):
    """ OpenVPN client_connect method
    """
    config = init_config(conf)
    nas_id = config.get('DEFAULT', 'nas_id')
    nas_addr = config.get('DEFAULT', 'nas_addr')
    secret = config.get('DEFAULT', 'radius_secret')
    radius_addr = config.get('DEFAULT', 'radius_addr')
    radius_acct_port = config.getint('DEFAULT', 'radius_acct_port')
    radius_timeout = config.getint('DEFAULT', 'radius_timeout')
    acct_interval = config.getint('DEFAULT', 'acct_interval')
    session_timeout = config.getint('DEFAULT', 'session_timeout')
    status_dbfile = config.get('DEFAULT', 'statusdb')

    username = os.environ.get('username')
    userip = os.environ.get('ifconfig_pool_remote_ip')
    realip = os.environ.get('trusted_ip')
    realport = os.environ.get('trusted_port')
    session_id = md5(nas_addr + realip + realport).hexdigest()

    req = {'User-Name':username}
    req['Acct-Status-Type'] = ACCT_START
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
    req["Framed-IP-Address"]  = userip

    def addonline(radresp):
        client = {}
        client['session_id'] = session_id
        client['username'] = username
        client['userip'] = userip
        client['realip'] = realip
        client['realport'] = realport
        client['ctime'] = int(time.time())
        client['inbytes'] = 0
        client['outbytes'] = 0
        try:
            client['acct_interval'] = tools.DecodeInteger(radresp.get(85)[0]) or 0
        except:
            client['acct_interval'] = acct_interval

        try:
            client['session_timeout'] = tools.DecodeInteger(radresp.get(27)[0]) or 0
        except:
            client['session_timeout'] = session_timeout

        statusdb.add_client(status_dbfile,client)
        log.msg('add new online<%s> client to db'%session_id)

    def shutdown(exitcode=0):
        reactor.addSystemEventTrigger('after', 'shutdown', os._exit,exitcode)
        reactor.stop()

    def onresp(r):
        try:
            addonline(r)
        except Exception as e:
            log.err('add client online error')
            log.err(e)
        shutdown(0)

    def onerr(e):
        log.err(e)
        shutdown(1)

    d = client.send_acct(str(secret), get_dictionary(), radius_addr, 
        acctport=radius_acct_port, debug=True,**req)
    d.addCallbacks(onresp,onerr)
    reactor.callLater(radius_timeout,shutdown,1)
    reactor.run()    


if __name__ == '__main__':
    cli()
