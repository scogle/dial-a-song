# gs.stream
# keep track of streaming songs

# from mc import GetApp
# from sys import path
# path.append(r'u:\apps\grooveshark\\')

# from util import getCountryCode, getBoxeeID, safe_str
from gs import service
# from definitions import *

class Stream(object):
    def __init__(self, item=None):
        self.item = item
        self.songID = 0
        self.streamServerID = 0
        self.streamKey = ''
        self.fetched = False
        self.error = 0
        self.reported30Secs = False
        self.reportedComplete = False
        self.reportedHistory = False
        self.retrys = 0
        self.resetPath()
        if item:
            songID = item.GetProperty('SongID')
            self.songID = int(songID)
            try:
                streamServerID = item.GetProperty('StreamServerID')
                self.streamServerID = int(streamServerID)
            except:
                self.streamServerID = 0
            self.streamKey = item.GetProperty('StreamKey')
            #self.fetched = item.GetPath() != 'app://%s/play' % GetApp().GetId()

    def getSongID(self):
        return self.songID

    def isValid(self):
        return self.songID > 0 and self.error == 0

    def clearStream(self):
        self.url = ''
        self.streamKey = ''
        self.streamServerID = 0
        self.resetPath()

    # def resetPath(self):
    #     if self.item:
    #         self.item.SetPath('app://%s/play' % GetApp().GetId()) 

    def fetchStream(self):
        countryCode = getCountryCode()
        uniqueID = getBoxeeID()
        request = service.Request('getSubscriberStreamKey', \
           {'songID': self.songID, 'lowBitrate': 'false', 'country': countryCode, 'uniqueID': uniqueID })
        if not request.hasError(): 
            self.url = safe_str(request.getResult('url'))
            self.item.SetPath(self.url)
            self.streamKey = request.getResult('StreamKey') 
            self.item.SetProperty('StreamKey', safe_str(self.streamKey))
            self.streamServerID = request.getResult('StreamServerID')
            self.item.SetProperty('StreamServerID', safe_str(self.streamServerID))
            self.fetched = True
        else:
            if self.retrys <= 5:
                self.retrys += 1
                self.fetchStream()
            else:
                self.error = 1

    def isFetched(self):
        return self.fetched

    def getItem(self):
        return self.item

    def report30Secs(self): 
        if not self.reported30Secs:
            print "%%%%%%%%%%%% Reporting 30sec"
            self.reported30Secs = True
            uniqueID = getBoxeeID()
            request = service.Request('markStreamKeyOver30Secs', \
                {'streamKey': self.streamKey, 'streamServerID': self.streamServerID, 'uniqueID': uniqueID }) 
            service.getTrial().songPlayed()
            print "%%%%%%%%%%%% Result: %s" % request.getResult('success')
            return request.getResult('success')
        return False

    def is30SecsReported(self):
        return self.reported30Secs

    def reportComplete(self):
        if not self.reportedComplete:
            print "%%%%%%%%%%%% Reporting Complete"
            request = service.Request('markSongComplete', \
                {'songID': self.songID, 'streamKey': self.streamKey, 'streamServerID': self.streamServerID})
            self.reportedComplete = True
            print "%%%%%%%%%%%% Result: %s" % request.getResult('success')
            return request.getResult('success')
        return False

    def isCompleteReported(self):
        return self.reportedComplete
 
    def setReportedHistory(self, report):
        self.reportedHistory = report

    def reportHistory(self):
        queue.getQueue().addHistory(self.item)

    def isHistoryReported(self):
        return self.reportedHistory

    def __str__(self):
        if self.isValid():
            return '%s: %s - %s' % (self.songID, self.item.GetArtist(), self.item.GetLabel())
        else:
            return 'song'
