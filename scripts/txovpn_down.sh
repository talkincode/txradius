#!/bin/sh

pgrep -f txovpn_daemon | xargs  kill

txovpn_initdb -c /etc/openvpn/txovpn.conf
