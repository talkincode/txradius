#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys,os
from twisted.python import log
from twisted.internet import reactor, defer,protocol
from twisted.internet.threads import deferToThread
from twisted.internet import utils as txutils
from txradius.radius import dictionary,packet
from txradius.openvpn import CONFIG_FILE,ACCT_UPDATE
from txradius.openvpn import get_challenge
from txradius.openvpn import get_dictionary
from txradius.openvpn import init_config
from txradius.openvpn import statusdb
from txradius import message, client
from hashlib import md5
import traceback
import click
import time
import six

def parse_status_file(status_file,nas_addr):
    ''' parse openvpn status log
    '''
    session_users = {}
    flag1 = False
    flag2 = False
    with open(status_file) as stlines:
        for line in stlines:

            if line.startswith("Common Name"):
                flag1 = True
                continue

            if line.startswith("ROUTING TABLE"):
                flag1 = False
                continue

            if line.startswith("Virtual Address"):
                flag2 = True
                continue

            if line.startswith("GLOBAL STATS"):
                flag2 = False
                continue

            if flag1:
                try:
                    username,realaddr,inbytes,outbytes,_ = line.split(',')
                    realip,realport = realaddr.split(':')
                    session_id = md5(nas_addr + realip + realport).hexdigest()
                    session_users.setdefault(session_id, {}).update(dict(
                        session_id=session_id,
                        username=username,
                        realip=realip,
                        realport=realport,
                        inbytes=inbytes,
                        outbytes=outbytes
                    ))
                except:
                    traceback.print_exc()

            if flag2:
                try:
                    userip,username,realaddr,_ = line.split(',')
                    realip,realport = realaddr.split(':')
                    session_id = md5(nas_addr + realip + realport).hexdigest()
                    session_users.setdefault(session_id, {}).update(dict(
                        session_id=session_id,
                        username=username,
                        realip=realip,
                        realport=realport,
                        userip=userip,
                    ))
                except:
                    traceback.print_exc()

    return session_users

def update_status(dbfile,status_file,nas_addr):
    ''' update status db
    '''
    try:
        total = 0
        params = []
        for sid, su in  parse_status_file(status_file, nas_addr).items():
            if 'session_id' in su and 'inbytes' in su and 'outbytes' in su:
                params.append((su['inbytes'],su['outbytes'],su['session_id']))
                total += 1
        statusdb.batch_update_client(dbfile,params)
        log.msg('update_status total = %s' % total)
    except Exception, e:
        log.err('batch update status error')
        log.err(e)

def accounting(dbfile,config):
    ''' update radius accounting
    '''
    try:
        nas_id = config.get('DEFAULT', 'nas_id')
        nas_addr = config.get('DEFAULT', 'nas_addr')
        secret = config.get('DEFAULT', 'radius_secret')
        radius_addr = config.get('DEFAULT', 'radius_addr')
        radius_acct_port = config.getint('DEFAULT', 'radius_acct_port')
        radius_timeout = config.getint('DEFAULT', 'radius_timeout')
        status_dbfile = config.get('DEFAULT', 'statusdb')

        clients = statusdb.query_client(status_dbfile)

        ctime = int(time.time())
        for cli in clients:
            if (ctime - int(cli['uptime'])) < int(cli['acct_interval']):
                continue

            session_id = cli['session_id']
            req = {'User-Name':cli['username']}
            req['Acct-Status-Type'] = ACCT_UPDATE
            req['Acct-Session-Id'] = session_id
            req["Acct-Output-Octets"]  =  int(cli['outbytes'])
            req["Acct-Input-Octets"]  =  int(cli['inbytes'])
            req['Acct-Session-Time'] = (ctime - int(cli['ctime']))
            req["NAS-IP-Address"]     = nas_addr
            req["NAS-Port-Id"]     = '0/0/0:0.0'
            req["NAS-Port"]           = 0
            req["Service-Type"]       = "Login-User"
            req["NAS-Identifier"]     = nas_id
            req["Called-Station-Id"]  = '00:00:00:00:00:00'
            req["Calling-Station-Id"] = '00:00:00:00:00:00'
            req["Framed-IP-Address"]  = cli['userip']

            def update_uptime(radresp):
                statusdb.update_client_uptime(status_dbfile,session_id)
                log.msg('online<%s> client accounting update'%session_id)

            def onresp(r):
                try:
                    update_uptime(r)
                except Exception as e:
                    log.err('online update uptime error')
                    log.err(e)

            d = client.send_acct(str(secret), get_dictionary(), radius_addr, 
                acctport=radius_acct_port, debug=True,**req)
            d.addCallbacks(onresp,log.err)

    except Exception, e:
        log.err('accounting error')
        log.err(e)


class Authorized(protocol.DatagramProtocol):

    def __init__(self, config):
        self.config = config
        self.dictionary = get_dictionary()
        self.radius_addr = config.get('DEFAULT', 'radius_addr')
        self.secret = config.get('DEFAULT', 'radius_secret')
        self.server_manage_addr = config.get('DEFAULT', 'server_manage_addr')
        self.status_dbfile = config.get('DEFAULT', 'statusdb')

    def get_killexe(self):
        if os.path.exists('/usr/bin/txovpn_kill'):
            return '/usr/bin/txovpn_kill'
        elif os.path.exists('/usr/local/bin/txovpn_kill'):
            return '/usr/local/bin/txovpn_kill'

    def processPacket(self, coareq, (host,port)):
        def coaresp(session):
            reply = coareq.CreateReply()
            reply.code = packet.DisconnectACK
            log.msg("[RADIUSAuthorize] :: Send Authorize radius response: %s" % (message.format_packet_str(reply)))
            self.transport.write(reply.ReplyPacket(),  (host, port))
            statusdb.del_client(self.status_dbfile, session.get('session_id'))

        saddr,sport = self.server_manage_addr.split(':')
        session = statusdb.get_client(self.status_dbfile,coareq.get_acct_sessionid())
        if session:
            clientstr = '{0}:{1}'.format(session['realip'],session['realport'])
            d = txutils.getProcessOutput(self.get_killexe(),args=('-s',saddr,'-p',sport,'-c',clientstr))
            d.addCallback(coaresp,session)
            d.addErrback(log.err)
        else:
            reply.code = packet.DisconnectNAK
            self.transport.write(reply.ReplyPacket(),  (host, port))


    def datagramReceived(self, datagram, (host, port)):
        try:
            if host not in self.radius_addr:
                log.err('[RADIUSAuthorize] :: Dropping Authorize packet from unknown host ' + host)
                return
            coa_req = message.CoAMessage(packet=datagram, dict=self.dictionary, secret=six.b(self.secret))
            log.msg("[RADIUSAuthorize] :: Received Authorize radius request : %s"%message.format_packet_str(coa_req))
            self.processPacket(coa_req,  (host, port))
        except Exception as err:
            log.err('RadiusError:Dropping invalid packet from {0} {1}'.format(host, port))
            log.err(err)



@click.command()
@click.option('-c','--conf', default=CONFIG_FILE, help='txovpn config file')
def main(conf):
    """ OpenVPN status daemon 
    """
    config = init_config(conf)
    nas_addr = config.get('DEFAULT', 'nas_addr')
    status_file = config.get('DEFAULT', 'statusfile')
    status_dbfile = config.get('DEFAULT', 'statusdb')
    nas_coa_port = config.get('DEFAULT', 'nas_coa_port')

    def do_update_status_task(): 
        d = deferToThread(update_status, status_dbfile, status_file, nas_addr)
        d.addCallback(log.msg,'do_update_status_task done!')
        d.addErrback(log.err)
        reactor.callLater(60.0,do_update_status_task)

    def do_accounting_task(): 
        d = deferToThread(accounting, status_dbfile, config)
        d.addCallback(log.msg,'do_accounting_task done!')
        d.addErrback(log.err)
        reactor.callLater(60.0,do_accounting_task)

    do_update_status_task()
    do_accounting_task()

    coa_protocol = Authorized(config)
    reactor.listenUDP(int(nas_coa_port), coa_protocol, interface='0.0.0.0')
    reactor.run()    


if __name__ == '__main__':
    main()
