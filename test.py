from twilio.rest import TwilioRestClient
from twilio import twiml
import service
from keys import *
from urllib import urlencode

account = TWILIO_ACCOUNT
token = TWILIO_TOKEN
client = TwilioRestClient(account, token)

service.Session().startSession()

numbers = [9704029786]

def call():
	for number in numbers:
		call = client.calls.create(to=number,
		                           from_="3522341775",
		                           # url="http://twimlets.com/holdmusic?Bucket=com.twilio.music.ambient"
		                           url = "http://pygmy.nfshost.com/pygmy.php"
		                           )

# def run():
#     print "sessionID: %s" % service.getSession().getSessionID()
#     request = service.Request('getStreamKeyStreamServer', {'songID':'24539127', 'country':{"ID":"223","CC1":"0","CC2":"0","CC3":"0","CC4":"1073741824","IPR":"82"}, 'lowBitrate':True})
#     if not request.hasError():
#         stream = request.getResult('url')
#         songURL = {'url':stream}
#         print songURL
#         # send dat url over to my server to generate some twiml
#         call(songURL)

call()