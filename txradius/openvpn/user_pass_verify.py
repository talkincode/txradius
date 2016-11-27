#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys,os
from twisted.python import log
from twisted.internet import reactor, defer
from twisted.python.logfile import DailyLogFile
from txradius.radius import dictionary,packet
from txradius.openvpn import CONFIG_FILE
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
    """ OpenVPN user_pass_verify method
    """
    config = readconfig(conf)
    if debug:
        log.startLogging(sys.stdout)
    else:
        log.startLogging(DailyLogFile.fromFullPath(config.get("DEFAULT",'logfile')))
    nas_id = config.get('DEFAULT', 'nas_id')
    nas_addr = config.get('DEFAULT', 'nas_addr')
    secret = config.get('DEFAULT', 'radius_secret')
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

    d = client.send_auth(str(secret), 
        get_dictionary(), radius_addr, authport=radius_auth_port, debug=True,**req)
    d.addCallbacks(onresp,onerr)
    reactor.run()    


if __name__ == '__main__':
    cli()
