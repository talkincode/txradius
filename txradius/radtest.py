#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys,os
from txradius import message, client
from txradius.radius import dictionary,packet
from twisted.internet import reactor, defer
from twisted.python import log
import functools
import click
import json
import random



# def send_auth(secret, dictionary, server, authport=1812, acctport=1813, debug=False, **kwargs):
#     return RadiusClient(secret, dictionary, server, authport, acctport, debug).sendAuth(**kwargs)

# def send_acct(secret, dictionary, server, authport=1812, acctport=1813, debug=False, **kwargs):
#     return RadiusClient(secret, dictionary, server, authport, acctport, debug).sendAcct(**kwargs)

def random_mac():
    mac = [ 0x52, 0x54, 0x00,
            random.randint(0x00, 0x7f),
            random.randint(0x00, 0xff),
            random.randint(0x00, 0xff) ]
    return ':'.join(map(lambda x: "%02x" % x, mac))

@click.group()
def cli():
    pass

@click.command()
@click.option('-h','--host', default='127.0.0.1',help="radius host")
@click.option('-p','--port', default=1812,help="radius auth port")
@click.option('-u','--username', default='test01',help="test auth username")
@click.option('-p','--password', default='888888',help="test auth password")
@click.option('-s','--secret', default='secret',help="radius secret")
@click.option('-e','--encrypt-type', default='pap',type=click.Choice(['pap','chap']))
def auth(host,port,username,password,secret,encrypt_type):
    """ radius auth testing """
    _dict =dictionary.Dictionary(os.path.join(os.path.dirname(client.__file__), "dictionary/dictionary"))
    req = {'User-Name':username}
    if encrypt_type == 'pap':
        req['User-Password'] = password
    else:
        req['CHAP-Challenge'] = '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        req['CHAP-Password'] = password

    req["NAS-IP-Address"]     = "192.168.1.10"
    req["NAS-Port"]           = 0
    req["Service-Type"]       = "Login-User"
    req["NAS-Identifier"]     = "trtest"
    req["Called-Station-Id"]  = random_mac()
    req["Calling-Station-Id"] = random_mac()
    req["Framed-IP-Address"]  = "10.0.0.100"
    print "radius auth: ",repr(req)
    def onresp(r):
        print message.format_packet_str(r)
        reactor.stop()

    sendauth = lambda : client.send_auth(str(secret), _dict, host, authport=port, debug=True,**req).addCallback(onresp)
    reactor.callLater(0.01, sendauth)
    reactor.run()

cli.add_command(auth)


if __name__ == '__main__':
    cli()