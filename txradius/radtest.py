#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys,os
from txradius import message, client
from txradius.radius import dictionary,packet
from twisted.internet import reactor, defer
from twisted.python import log
import functools
import click
import random

ACCT_TYPES = ['start','stop','update','bason','basoff']
ACCT_TYPE_MAP = {'start':1,'stop':2,'update':3,'bason':7,'basoff':8}

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

    req["NAS-IP-Address"]     = "10.10.10.1"
    req["NAS-Port"]           = 0
    req["Service-Type"]       = "Login-User"
    req["NAS-Identifier"]     = "trtest"
    req["Called-Station-Id"]  = random_mac()
    req["Calling-Station-Id"] = random_mac()
    req["Framed-IP-Address"]  = "10.0.0.%s"% random.randint(2,254)
    print "radius auth: ",repr(req)
    def onresp(r):
        print message.format_packet_str(r)
        reactor.stop()

    sendauth = lambda : client.send_auth(str(secret), _dict, host, authport=port, debug=True,**req).addCallback(onresp)
    reactor.callLater(0.01, sendauth)
    reactor.run()


@click.command()
@click.option('-h','--host', default='127.0.0.1',help="radius host")
@click.option('-p','--port', default=1813,help="radius acct port")
@click.option('-t','--acct-type', default='start',type=click.Choice(ACCT_TYPES),help="radius acct type")
@click.option('-u','--username', default='test01',help="test acct username")
@click.option('-s','--secret', default='secret',help="radius secret")
def acct(host,port,acct_type,username,secret):
    """ radius acct testing """
    _dict =dictionary.Dictionary(os.path.join(os.path.dirname(client.__file__), "dictionary/dictionary"))
    req = {'User-Name':username}
    req['Acct-Status-Type'] = ACCT_TYPE_MAP[acct_type]
    req["Acct-Output-Octets"]  =  random.randint(10240, 8192000)
    req["Acct-Input-Octets"]  =  random.randint(10240, 819200)
    req['Acct-Session-Time'] = random.randint(300, 3600)
    req["NAS-IP-Address"]     = "10.10.10.1"
    req["NAS-Port"]           = 0
    req["Service-Type"]       = "Login-User"
    req["NAS-Identifier"]     = "trtest"
    req["Called-Station-Id"]  = random_mac()
    req["Calling-Station-Id"] = random_mac()
    req["Framed-IP-Address"]  = "10.0.0.%s"% random.randint(2,254)
    print "radius acct: ",repr(req)
    def onresp(r):
        print message.format_packet_str(r)
        reactor.stop()

    sendacct = lambda : client.send_acct(str(secret), _dict, host, acctport=port, debug=True,**req).addCallback(onresp)
    reactor.callLater(0.01, sendacct)
    reactor.run()


cli.add_command(auth)
cli.add_command(acct)


if __name__ == '__main__':
    cli()