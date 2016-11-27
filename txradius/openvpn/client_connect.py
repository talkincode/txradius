#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys,os
from twisted.python import log
from twisted.internet import reactor, defer
from twisted.python.logfile import DailyLogFile
from txradius.radius import dictionary,packet
from txradius.openvpn import CONFIG_FILE,ACCT_START
from txradius.openvpn import get_challenge
from txradius.openvpn import get_dictionary
from txradius.openvpn import readconfig
from txradius import message, client
import traceback
import click

@click.command()
@click.option('-c','--conf', default=CONFIG_FILE, help='txovpn config file')
@click.option('-d','--debug', is_flag=True)
def cli(conf,debug):
    """ OpenVPN client_connect method
    """
    config = readconfig(conf)
    log.startLogging(DailyLogFile.fromFullPath(config.get("DEFAULT",'logfile')))
    nas_id = config.get('DEFAULT', 'nas_id')
    nas_addr = config.get('DEFAULT', 'nas_addr')
    secret = config.get('DEFAULT', 'radius_secret')
    radius_addr = config.get('DEFAULT', 'radius_addr')
    radius_acct_port = config.get('DEFAULT', 'radius_acct_port')

    session_id = 0
    req = {'User-Name':os.environ.get('username')}
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


if __name__ == '__main__':
    cli()
