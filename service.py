# gs.service
# access point to grooveshark's api

from hmac import new
import simplejson as json
from urllib import urlencode
from urllib2 import Request as req, urlopen
from time import time
import simplejson as json
from simplejson import loads

# from sys import path
# path.append(r'u:\apps\grooveshark\\')

# import util
# from gs.grooveshark import getGrooveshark
# from definitions import *
import time

from keys import *


def getSession():
    global _session
    try:
        if not _session:
            _session = Session()
    except:
        _session = Session()
    return _session

class Session(object):
    def __init__(self):
        self.sessionID = '41ae21cfd8c3148dbf8b59e98fb90088'
        self.login = GS_LOGIN
        self.password = GS_PASSWORD

    def startSession(self):
        request = SecureRequest('startSession')

        # print "sessionID: %s" % request.getResult()


    def getSessionID(self):
        # if self.sessionID:
        #     return self.sessionID
        # else:
        #     self.startSession()
        #     return self.sessionID
        return self.sessionID

    def hasSessionID(self):
        # if self.sessionID is not '':
        #     return True
        return True


class Request(object):
    def __init__(self, method, params={}, autoRequest=True):
        # self.user = getGrooveshark().getUser()
        self.PROTOCOL = 'http'
        self.HOST = GS_API
        self.ENDPOINT = GS_ENDPOINT
        self.WSKEY = GS_WSKEY
        self.TOKEN = GS_TOKEN

        self.response = ''
        self.decoded = ''
        self.message = ''
        self.code = 0

        self.method = method
        self.params = params
        self.header = {'wsKey': self.WSKEY}

        if getSession().hasSessionID():
            self.refreshHeader()
 
        if autoRequest:
            self.sendRequest()

    def refreshHeader(self):
        """ has to be dynamic in case the session changes """
        if getSession().hasSessionID():
            self.header['sessionID'] = getSession().getSessionID()

    def getSignature(self):
        # hmac.new
        return new(self.TOKEN, self.getRequest()).hexdigest()

    def getRequest(self):
        self.refreshHeader()
        return json.dumps({'method': self.method, 'header': self.header, 'parameters': self.params})

    def sendRequest(self):
        url = '%s://%s/%s?sig=%s' % (self.PROTOCOL, self.HOST, self.ENDPOINT, self.getSignature())
        try:
            #req() is urllib2.Request()
            request = req(url, self.getRequest())
            self.response = urlopen(request)
        except Exception, e:
            pass
            #mc.GetApp().Close()
        try: 
            self.decoded = json.loads(self.response.read())
        except:
            self.error = 9000
            self.message = 'malformed response'
            return
        if self.decoded.has_key('errors'):
            self.code = self.decoded['errors'][0]['code']
            self.message = self.decoded['errors'][0]['message']
            # if self.code == 300: # session is stale
            #     self.user.requestSession()
            #     if self.user.reauthenticate():
            #         self.request()
            #     else:
            #         #GetActiveWindow().PopState(False)
            #         #getGrooveshark().logout()
            #         #ShowDialogOk("Session Expired", "Your session has expired and your login credentials have since changed. Please re-enter your credentials.")
            #         return 
            # elif self.code in [104, 105]: 
            #     trial = getTrial()
            #     trial.setEnded(True)
            #     trial.showTrialEnded()
            #     from mc import GetPlayer, PlayList
            #     GetPlayer().Stop()
            #     PlayList().Clear()
            # elif self.code in [102, 103, 104]:
            #     trial = getTrial()
            #     if not trial.isStarted():
            #         trial.showTrialNotStarted()
            #     else:
            #         self.setEnded(True)
            #         trial.showTrialEnded()
            # elif self.code == 11:
            #     notify("Too many streams have failed! Let's chill out for a bit.")
            #     from mc import GetPlayer
            #     GetPlayer().Stop()
            #     getGrooveshark().getPlayer().getQueue().generatePlaylist()

    def hasError(self):
        """ Returns if error occurred. """
        return int(self.code) > 0

    def getCode(self):
        """ Return error code. """
        return self.code

    def getMessage(self):
        """ Return error message. """
        return self.message

    def getRaw(self):
        """ Get raw service return. """
        return self.response

    def getResult(self, key=None):
        """ Get decoded service return. """
        if self.hasError():
            return None
        try:
            if not key:
                return self.decoded['result']
            else:
               return self.decoded['result'].get(key, '')
        except:
            return None

class SecureRequest(Request):
    def __init__(self, method, params={}, autoRequest=True):
        Request.__init__(self, method, params, False)
        self.PROTOCOL = 'https'

        if autoRequest:
            self.sendRequest()
