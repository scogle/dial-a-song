from twilio.rest import TwilioRestClient
from twilio import twiml
import service
from keys import *

account = TWILIO_ACCOUNT
token = TWILIO_TOKEN
client = TwilioRestClient(account, token)

service.Session().startSession()

def call():
	call = client.calls.create(to="9704029786", 
	                           from_="4155992671", 
	                           url="http://twimlets.com/holdmusic?Bucket=com.twilio.music.ambient"
	                           # url = "callResponse.py"
	                           )

def run():
	print "sessionID: %s" % service.getSession().getSessionID()
	

#run()
call()