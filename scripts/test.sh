#!/bin/bash

auth()
{
    export username=test01
    export password=888888
    export ifconfig_pool_remote_ip=10.8.0.11
    export trusted_ip=192.168.100.9
    export trusted_port=10011
    txovpn_auth
}


connect()
{
    export username=test01
    export password=888888
    export ifconfig_pool_remote_ip=10.8.0.11
    export trusted_ip=192.168.100.9
    export trusted_port=10011    
    txovpn_connect
}



disconnect()
{
    export username=test01
    export password=888888
    export ifconfig_pool_remote_ip=10.8.0.11
    export trusted_ip=192.168.100.9
    export trusted_port=10011    
    txovpn_disconnect
}


case "$1" in

  auth)
    auth
  ;;

  conn)
    connect
  ;;

  disc)
    disconnect
  ;;

  initdb)
    txovpn_initdb
  ;;

esac

