# Grooveshark on Boxee
# Player

import mc
from threading import Thread
from time import sleep

from sys import path
path.append(r'u:\apps\grooveshark\\')

from util import notify
import stream, service
from page import ui
from definitions import *
from model import queue as q, autoplay

def getPlayer():
    global _player
    try:
        if not _player :
            _player = Player()
    except:
        _player = Player()
    return _player

class Player(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.player = mc.Player(True)
        self.numFailures = 0
        self.ready = False
        self.readyPosition = -1 
        self.running = False # thread state
        self.completed = False # Flag to see if playlist has completed
        print "$$$$$$$$$$$ Hello!"

    def setQueue(self, queue):
        self.queue = queue

    def getQueue(self):
        return self.queue

    def isComplete(self):
        return self.completed

    def play(self, position=-1):
        """ this command comes from queue, usually """
        self.ready = True
        #self.readyPosition = self.queue.getPlaylistPosition(position)
        self.readyPosition = position

    def start(self):
        if not self.queue:
            return False
	self.player.SetLastPlayerEvent(mc.Player.EVENT_NONE)
        self.running = True
        Thread.start(self)
        return True
    

    def startAutoplay(self, tagID=0):
        if tagID:
            request = service.Request('startAutoplayTag', {'tagID': tagID})
            if not request.hasError():
                state = request.getResult('autoplayState')
                a = autoplay.Autoplay(state)
                song = a.getNextSong()
                newQueue = q.RadioQueue()
                newQueue.setAutoplay(a)
                newQueue.append(song)
                self.setQueue(newQueue)
                self.play(0)
        else: # regular ol' autoplay.
            artistIDs = []
            songIDs = []
            songs = self.queue.getItems()
            for song in songs:
                artistIDs.append(song['ArtistID'])
                songIDs.append(song['SongID'])
            request = service.Request('startAutoplay', \
                {'artistIDs': artistIDs, 'songIDs': songIDs})
            if not request.hasError():
                state = request.getResult('autoplayState')
                nextSong = request.getResult('nextSong')
                a = autoplay.Autoplay(state)
                newQueue = q.RadioQueue()
                newQueue.setAutoplay(a)
                # songs.append(nextSong)
                newQueue.append(songs)
                for songID in songIDs:
                    newQueue.setVoteState(songID)
                self.setQueue(newQueue)
                ui.getPage().setList(newQueue)
                ui.getPage().prepare()
                ui.getPage().render()
  
    def stopAutoplay(self):
        newQueue = q.Queue()
        newQueue.setItems(self.queue.getItems())
        self.setQueue(newQueue)
        # newQueue.removeByIndex(self, len(self.items)-1)
        ui.getPage().setList(self.queue)
        ui.getPage().prepare()
        ui.getPage().render()

    def kill(self):
        self.running = False

    def run(self):
        current = stream.Stream()
        next = stream.Stream()
        position = -1

        while self.running:
            sleep(1)
            # catch end of playlist for repeats...
            if self.queue.isRepeat() and self.queue.getPlaylistPosition() == -1 and position == self.queue.size() - 1:
                position = -1
                self.queue.generatePlaylist()
                self.play(0)
                continue
            if position != self.queue.getPlaylistPosition() and self.queue.getPlaylistPosition() >= 0:
                if self.queue.getPlaylistPosition() not in [position + 1, self.readyPosition, -1, position - 1] and mc.GetPlayer().GetLastPlayerEvent() == mc.GetPlayer().EVENT_NONE:
                    previous = self.queue.getPlaylistItem(self.queue.getPlaylistPosition() - 1)
                    notify('Could not stream %s - %s.' % (previous.GetArtist(), previous.GetTitle()))
                position = self.queue.getPlaylistPosition()
                if position < self.queue.size():
                    current = stream.Stream(self.queue.getPlaylistItem(position))
                else:
                    current = stream.Stream()
                if current.isValid():
                    current.resetPath() # kill stale streams for prev/next
                    queuePos = self.queue.getQueuePosition()
                    item = self.queue.getItems()[position]
                    nowplaying = self.queue.getListItemFromItem(item)
                    ui.updateNowPlaying(nowplaying)
                
                if position + 1 < self.queue.size():
                    next = stream.Stream(self.queue.getPlaylistItem(position + 1))
                else:
                    if self.queue.isRadio():
                        self.queue.resetRecommendation()
                        self.queue.generateListItems()
                        ui.refresh()
                    next = stream.Stream()
            if self.ready:
                self.ready = False
                if self.readyPosition < 0:
                    self.readyPosition = self.queue.getPlaylistPosition()
                    if self.player.IsPlaying():
                        self.readyPosition += 1
                self.player.PlaySelected(self.readyPosition)
            # check if grooveshark is still open
            #elif mc.GetApp().GetId() != service.APP_ID:
            #    self.kill()
            # check and act on player actions while player is playing
            elif self.player.GetLastPlayerEvent() == mc.Player.EVENT_STARTED:
                # retrieve elapsed time
                try:
                    elapsed = self.player.GetTime()
                    total = self.player.GetTotalTime()
                except:
                    elapsed = 0
                    total = 0
                # 30 seconds elapsed, report fact
                if elapsed >= 30 and not current.is30SecsReported():
                    current.report30Secs()
                    request = service.GutsRequest('markStreamKey30secs', 'mark30secs:true')
                # 30 seconds left, attempt prefetch
                # prefetching is forcing a stream fail/retry. removing for now
                elif elapsed >= (total - 30.0) and next.isValid() and not next.isFetched():
                    next.fetchStream()
                # check if we have a song to stream now...
                elif elapsed >= (total - 30.0) and not next.isValid():
                    nextSong = self.queue.getPlaylistItem(position + 1)
                    if nextSong:
                        try:
                            next = stream.Stream(nextSong)
                            next.fetchStream()
                            self.completed = False # If there's a next song, then the plist hasn't completed
                        except:
                            self.completed = True # An exception is thrown when the playlist finishes.  Ugly but it works.
                            self.getQueue().generatePlaylist()
                # very end of the song, report
                elif elapsed >= (total - 10.1):
                    current.reportComplete()
