import service
from twilio import twiml

streamURL = ''

request = service.Request('getStreamKeyStreamServer', {'songID':'29689131', 'country':{"ID":"223","CC1":"0","CC2":"0","CC3":"0","CC4":"1073741824","IPR":"82"}})
        if not request.hasError():
            streamURL = request.getResult('url')
            r = twiml.Response()
            r.play(streamURL)
            print str(r)
        else:
        	r = twiml.Response()
        	r.say('ERROR! ERROR! ERROR!')
        	print str(r)

