import sys,os
sys.path.insert(0, "../../")
from txradius import message, client
from txradius.radius import dictionary,packet
from twisted.internet import reactor, defer
from twisted.python import log
import functools

log.startLogging(sys.stderr)



@defer.inlineCallbacks
def test_auth():
    _dict =dictionary.Dictionary('../../dictionary/dictionary')
    sender = functools.partial(client.send_auth,'secret',_dict,"127.0.0.1")

    req = {}
    req['User-Name'] = 'test01'
    req['CHAP-Password'] = '888888'
    req["NAS-IP-Address"]     = "192.168.1.10"
    req["NAS-Port"]           = 0
    req["Service-Type"]       = "Login-User"
    req["NAS-Identifier"]     = "trillian"
    req["Called-Station-Id"]  = "00-04-5F-00-0F-D1"
    req["Calling-Station-Id"] = "00-01-24-80-B3-9C"
    req["Framed-IP-Address"]  = "10.0.0.100"
    log.msg("req:"+ repr(req))
    resp = yield sender(**req)
    log.msg('auth done %s'% repr(resp))
    reactor.stop()

reactor.callLater(0.1, test_auth,)
reactor.run()





