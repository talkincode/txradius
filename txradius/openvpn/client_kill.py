#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import click
import telnetlib

@click.command()
@click.option('-s','--server', default='127.0.0.1',help='openvpn server addr')
@click.option('-p','--port', default=7505,type=click.INT,help='openvpn server manage port')
@click.option('-c','--client', default=None, help='client addr x.x.x.x:xxxx')
def cli(server,port,client):
    """ OpenVPN client_kill method
    """
    tn = telnetlib.Telnet(host=server,port=port)
    tn.write('kill %s\n'%client.encode('utf-8'))
    tn.write('exit\n')
    os._exit(0)


if __name__ == '__main__':
    cli()
