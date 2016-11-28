#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys,os
from twisted.python import log
from twisted.internet import reactor, defer
from twisted.python.logfile import DailyLogFile
from txradius.radius import dictionary,packet
from txradius.openvpn import CONFIG_FILE,ACCT_STOP
from txradius.openvpn import get_challenge
from txradius.openvpn import get_dictionary
from txradius.openvpn import readconfig
from txradius import message, client
from txradius.openvpn import statusdb
from hashlib import md5
import traceback
import click

@click.command()
@click.option('-c','--conf', default=CONFIG_FILE, help='txovpn config file')
def cli(conf):
    """ OpenVPN client_disconnect method
    """
    config = readconfig(conf)
    debug = config.getboolean('DEFAULT', 'debug')
    if debug:
        log.startLogging(sys.stdout)
    else:
        log.startLogging(DailyLogFile.fromFullPath(config.get("DEFAULT",'logfile')))

    nas_id = config.get('DEFAULT', 'nas_id')
    secret = config.get('DEFAULT', 'radius_secret')
    nas_addr = config.get('DEFAULT', 'nas_addr')
    radius_addr = config.get('DEFAULT', 'radius_addr')
    radius_acct_port = config.getint('DEFAULT', 'radius_acct_port')
    radius_timeout = config.getint('DEFAULT', 'radius_timeout')
    status_dbfile = config.get('DEFAULT', 'statusdb')

    username = os.environ.get('username')
    userip = os.environ.get('ifconfig_pool_remote_ip')
    realip = os.environ.get('trusted_ip')
    realport = os.environ.get('trusted_port')
    session_id = md5(nas_addr + realip + realport).hexdigest()

    req = {'User-Name':username}
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
    req["Framed-IP-Address"]  = userip
 
    def shutdown(exitcode=0):
        reactor.addSystemEventTrigger('after', 'shutdown', os._exit,exitcode)
        reactor.stop()

    def onresp(r):
        try:
            statusdb.del_client(status_dbfile,session_id)
            log.msg('delete online<%s> client from db'%session_id)
        except Exception as e:
            log.err('del client online error')
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
