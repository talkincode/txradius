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
import time

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
@click.option('--nas-ip', default='10.0.0.1')
@click.option('--user-ip', default='10.0.0.100')
def auth(host,port,username,password,secret,encrypt_type,nas_ip,user_ip):
    """ radius auth testing """
    _dict =dictionary.Dictionary(os.path.join(os.path.dirname(client.__file__), "dictionary/dictionary"))
    req = {'User-Name':username}
    if encrypt_type == 'pap':
        req['User-Password'] = password
    else:
        req['CHAP-Challenge'] = '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        req['CHAP-Password-Plaintext'] = password

    req["NAS-IP-Address"]     = nas_ip
    req["NAS-Port-Id"]     = '3/0/1:0.0'
    req["NAS-Port"]           = 0
    req["Service-Type"]       = "Login-User"
    req["NAS-Identifier"]     = "trtest"
    req["Called-Station-Id"]  = random_mac()
    req["Calling-Station-Id"] = random_mac()
    req["Framed-IP-Address"]  = user_ip
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
@click.option('--session-id', default='session-00001')
@click.option('--nas-ip', default='10.0.0.1')
@click.option('--user-ip', default='10.0.0.100')
def acct(host,port,acct_type,username,secret,
    session_id,nas_ip,user_ip):
    """ radius acct testing """
    _dict =dictionary.Dictionary(os.path.join(os.path.dirname(client.__file__), "dictionary/dictionary"))
    req = {'User-Name':username}
    req['Acct-Status-Type'] = ACCT_TYPE_MAP[acct_type]
    req['Acct-Session-Id'] = session_id
    req["Acct-Output-Octets"]  =  4096
    req["Acct-Input-Octets"]  =  1024 
    req['Acct-Session-Time'] = int(time.time())%1999
    req["NAS-IP-Address"]     = nas_ip
    req["NAS-Port-Id"]     = '3/0/1:0.0'
    req["NAS-Port"]           = 0
    req["Service-Type"]       = "Login-User"
    req["NAS-Identifier"]     = "trtest"
    req["Called-Station-Id"]  = random_mac()
    req["Calling-Station-Id"] = random_mac()
    req["Framed-IP-Address"]  = user_ip
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