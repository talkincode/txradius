#!/bin/sh

if [ $( pgrep -f txovpn_daemon | wc -l ) -gt 0 ];then
    pgrep -f txovpn_daemon | xargs  kill
fi
txovpn_initdb -c /etc/openvpn/txovpn.conf
