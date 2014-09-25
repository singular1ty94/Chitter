import os, os.path
import cherrypy
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener

from naives import *
import json

# OUR TWITTER KEYS
ckey = 'MIoBpZbjBmRfH1ToD5oIuBOEk'
csecret = 'qi37rRfdH3A8EHVCADKsfQJ045MjdYynV1xWAcWk394cIoXoXW'
atoken = '182779783-LNZwsHtGLECvQfhcbD9UtlbjReyLkS7jNHFOiNjD'
asecret = 'XSn95pTAyqhzyfoVhyGdEP6uu5ShbegQ8AGi4zkH5npkg'

#Tweets array
tweets = []
stop = False

# Simple Class for Listening to
# the stream.
class listener(StreamListener):

	def on_data(self, data):
		global stop
		if stop is False:
			tweets.append(data)
			return True
		else:
			return False

	def on_error(self, status):
		print status

# Set up the core features, but don't stream yet.
auth = OAuthHandler(ckey, csecret)
auth.set_access_token(atoken, asecret)

#Global twitter stream
twitterStream = None;

##
# The Chitter Web Server
##
class Chitter(object):
	runOnce = False
	
	@cherrypy.expose
	def index(self):
   		f = open('public/index.html', 'r')
   		return f.read()
   		
   	@cherrypy.expose
   	def prepare(self, search=""):
   		global twitterStream, tweets, stop
   		tweets = []
   		stop = False
   		
   		# Just in case it's a comma-delimited list, split it.
   		arr = search.split(',');
   		arr[:] = [item.strip() for item in arr]		

   		twitterStream = Stream(auth, listener())
		twitterStream.filter(track=arr)
		return "Streaming"
   		
   	@cherrypy.expose
   	def stream(self):
   		global tweets
   		try:   	
   			temp = tweets.pop(0)
   			test = json.loads(temp)
   			modified = test['text'] + " - " + testTweet(classifier,test['text'])
   			test['text'] =  modified
   			return json.dumps(test)
		except:
			pass
			
	@cherrypy.expose
	def stop(self):
		global twitterStream, tweets, stop
		stop = True		
		tweets = []
   		

##
# Standard setup for the simple web server.
#
# Sets the static folders under the /public route.
##
if __name__ == '__main__':
	conf = {
		'/': {
			'tools.sessions.on': True,
            'tools.staticdir.root': os.path.abspath(os.getcwd())
         },
         '/static': {
             'tools.staticdir.on': True,
             'tools.staticdir.dir': './public'
         }
    }
	cherrypy.quickstart(Chitter(), '/', conf)