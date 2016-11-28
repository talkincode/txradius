#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys,os
from twisted.python import log
from twisted.internet import reactor, defer
from txradius.radius import dictionary,packet,tools
from txradius.openvpn import CONFIG_FILE
from txradius.openvpn import get_challenge
from txradius.openvpn import get_dictionary
from txradius.openvpn import init_config
from txradius import message, client
import traceback
import click

def get_radius_addr_attr(r,code,defval=None):
    try:
        return tools.DecodeAddress(r.get(code)[0])
    except:
        traceback.print_exc()
        return defval

@click.command()
@click.option('-c','--conf', default=CONFIG_FILE, help='txovpn config file')
def cli(conf):
    """ OpenVPN user_pass_verify method
    """
    config = init_config(conf)
    nas_id = config.get('DEFAULT', 'nas_id')
    nas_addr = config.get('DEFAULT', 'nas_addr')
    secret = config.get('DEFAULT', 'radius_secret')
    radius_addr = config.get('DEFAULT', 'radius_addr')
    radius_auth_port = config.getint('DEFAULT', 'radius_auth_port')
    radius_timeout = config.getint('DEFAULT', 'radius_timeout')
    client_config_dir = config.get('DEFAULT', 'client_config_dir')

    username = os.environ.get('username')

    req = {'User-Name':username}
    req['CHAP-Challenge'] = get_challenge()
    req['CHAP-Password-Plaintext'] = os.environ.get('password')
    req["NAS-IP-Address"]     = nas_addr
    req["NAS-Port-Id"]     = '0/0/0:0.0'
    req["NAS-Port"]           = 0
    req["Service-Type"]       = "Login-User"
    req["NAS-Identifier"]     = nas_id
    req["Called-Station-Id"]  = '00:00:00:00:00:00'
    req["Calling-Station-Id"] = '00:00:00:00:00:00'
    # req["Framed-IP-Address"]  = os.environ.get('ifconfig_pool_remote_ip')
    # log.msg("radius auth: %s" % repr(req))

    def shutdown(exitcode=0):
        reactor.addSystemEventTrigger('after', 'shutdown', os._exit,exitcode)
        reactor.stop()

    def onresp(r):
        if r.code == packet.AccessAccept:
            try:
                ccdattrs = []
                userip = get_radius_addr_attr(r,8)
                if userip:
                    ccdattrs.append('ifconfig-push {0} 255.255.255.0'.format(userip))
                with open(os.path.join(client_config_dir,username),'wb') as ccdfs:
                    ccdfs.write('\n'.join(ccdattrs))
            except:
                traceback.print_exc()
            shutdown(0)
        else:
            shutdown(1)
            
    def onerr(e):
        log.err(e)
        shutdown(1)

    d = client.send_auth(str(secret), 
        get_dictionary(), radius_addr, authport=radius_auth_port, debug=True,**req)
    d.addCallbacks(onresp,onerr)
    reactor.callLater(radius_timeout,shutdown,1)
    reactor.run()    


if __name__ == '__main__':
    cli()
