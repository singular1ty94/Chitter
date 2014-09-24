import os, os.path
import cherrypy
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener

# OUR TWITTER KEYS
ckey = 'TfbXbyPI2hF6IEpNtrzGBxXET'
csecret = 'Qtb1vPdM7YSqcXKAdQkZ15MSuXYUzrH9Piv5ddBi6uF2gES3Fh'
atoken = '615738366-ZPmyGEWqxVNkW2UFLSmH7HadACsM2kupw1Gf6QAR'
asecret = 'oWOi5LppyKm5ApmCQoHpKMfzARcstinukMLmuuiaRl31E'

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
			print data
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
   			return tweets.pop(0)
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