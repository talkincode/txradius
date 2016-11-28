#!/bin/sh

echo 'openvpn up'

txovpn_initdb -c /etc/openvpn/txovpn.conf

nohup txovpn_daemon > /dev/null 2>&1 &