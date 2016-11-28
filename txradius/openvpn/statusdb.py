#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import click
import sqlite3
import traceback
from txradius.openvpn import CONFIG_FILE
from txradius.openvpn import readconfig

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def get_conn(dbfile):
    conn = sqlite3.connect(dbfile)
    conn.row_factory = dict_factory
    return conn

def add_client(dbfile,client={}):
    try:
        conn = get_conn(dbfile)
        cur = conn.cursor()
        sqlstr = '''insert into client_status
        values (?,?,?,?,?,?,?,?,?,?,?)
        '''
        params = (
            client['session_id'],
            client['username'],
            client['userip'],
            client['realip'],
            int(client['realport']),
            client['ctime'],
            client['inbytes'],
            client['outbytes'],
            client['acct_interval'],
            client['session_timeout'],
            int(time.time())
        )
        cur.execute("delete from client_status where session_id=:sid",{'sid':client['session_id']})
        cur.execute(sqlstr,params)
        conn.commit()
        conn.close()
    except Exception, e:
        traceback.print_exc()


def update_client(dbfile,session_id,inbytes,outbytes):
    try:
        conn = get_conn(dbfile)
        cur = conn.cursor()
        sqlstr = '''update client_status 
        set inbytes=:inbytes, outbytes=:outbytes
        where session_id=:session_id'''
        params = dict(session_id=session_id,inbytes=inbytes,outbytes=outbytes)
        cur.execute(sqlstr,params)
        conn.commit()
        conn.close()
    except Exception, e:
        traceback.print_exc()


def update_client_uptime(dbfile,session_id):
    try:
        conn = get_conn(dbfile)
        cur = conn.cursor()
        sqlstr = '''update client_status set uptime=:uptime where session_id=:session_id'''
        params = dict(session_id=session_id,uptime=int(time.time()))
        cur.execute(sqlstr,params)
        conn.commit()
        conn.close()
    except Exception, e:
        traceback.print_exc()


def batch_update_client(dbfile,params=[]):
    try:
        conn = get_conn(dbfile)
        cur = conn.cursor()
        sqlstr = '''update client_status set inbytes=?, outbytes=? where session_id=?'''
        cur.executemany(sqlstr,params)
        conn.commit()
        conn.close()
    except Exception, e:
        traceback.print_exc()



def query_client(dbfile):
    try:
        conn = get_conn(dbfile)
        cur = conn.cursor()
        sqlstr = '''select * from client_status order by ctime desc '''
        cur.execute(sqlstr)
        result = cur.fetchall()
        conn.commit()
        conn.close()
        return result
    except Exception, e:
        traceback.print_exc()


def del_client(dbfile,session_id):
    try:
        conn = get_conn(dbfile)
        cur = conn.cursor()
        sqlstr = 'delete from client_status where session_id=:session_id'
        cur.execute(sqlstr,dict(session_id=session_id))
        conn.commit()
        conn.close()
    except Exception, e:
        traceback.print_exc()

@click.command()
@click.option('-c','--conf', default=CONFIG_FILE, help='txovpn config file')
def list(conf):
    """ OpenVPN status list method
    """
    try:
        config = readconfig(conf)
        conn = get_conn(config.get('DEFAULT','statusdb'))
        cur = conn.cursor()
        sqlstr = '''select * from client_status order by ctime desc '''
        cur.execute(sqlstr)
        result = cur.fetchall()
        conn.commit()
        conn.close()
        for r in result:
            print r
    except Exception, e:
        traceback.print_exc()


@click.command()
@click.option('-c','--conf', default=CONFIG_FILE, help='txovpn config file')
def cli(conf):
    """ OpenVPN status initdb method
    """
    try:
        config = readconfig(conf)
        debug = config.getboolean('DEFAULT', 'debug')
        conn = get_conn(config.get('DEFAULT','statusdb'))
        cur = conn.cursor()
        sqlstr = '''create table client_status
        (session_id text PRIMARY KEY, username text, userip text, 
            realip text, realport int,ctime int,
            inbytes int, outbytes int, 
            acct_interval int, session_timeout int, uptime int)
        '''
        try:
            cur.execute('drop table client_status')
        except:
            pass
        cur.execute(sqlstr)
        print 'flush client status database'
        conn.commit()
        conn.close()
    except:
        traceback.print_exc()


if __name__ == '__main__':
    cli()
