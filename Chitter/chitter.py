import os, os.path
import cherrypy
from naives import *
import json
import subprocess
from metrics import *
from twython import Twython

# OUR TWITTER KEYS
ckey = 'MIoBpZbjBmRfH1ToD5oIuBOEk'
csecret = 'qi37rRfdH3A8EHVCADKsfQJ045MjdYynV1xWAcWk394cIoXoXW'

#Used for the twython rest
tweetsREST = []
searchREST = ""


##
# The Chitter Web Server
##
class Chitter(object):
	runOnce = False
	
	@cherrypy.expose
	def index(self):
   		f = open('public/index.html', 'r')
   		html = f.read()
   		f.close()
   		return html
   				
	@cherrypy.expose
	def dashboard(self):
		#finalize the lang
		saveMetrics()
		
		f = open('public/dashboard.html', 'r')
   		html = f.read()
   		f.close()
   		return html
   		
   	@cherrypy.expose
   	def rest(self, search=""):
   		global tweetsREST, searchREST
   		tweetsREST = []
   		#READ ONLY ACCESS
		#Rate Limited to 450/queries/15 mins
		#ie 1800 per hour @ max 100 tweets each request.
		twitter = Twython(ckey, csecret, oauth_version=2)
		ACCESS = twitter.obtain_access_token()
		twitter = Twython(ckey, access_token=ACCESS)

		#Search as requested.
		searchREST = search
		tweet = twitter.search(q=search, count=100)
		tweetsREST[:] = [t['text'] for t in tweet['statuses']]

				
	@cherrypy.expose
   	def streamREST(self):
   		global tweetsREST, searchREST
   		
   		#Exactly ten, Only do on 10
   		if len(tweetsREST) == 10:
   			twitter = Twython(ckey, csecret, oauth_version=2)
			ACCESS = twitter.obtain_access_token()
			twitter = Twython(ckey, access_token=ACCESS)
			tweet = twitter.search(q=searchREST, count=100)
			tweetsREST[:] = [t['text'] for t in tweet['statuses']]
   		
   		try:
			# temporary needs proper variable
			temp = tweetsREST.pop(0)
			simple = {"text":""}
			
			## GET SENTIMENT ##
			senti = testTweet(classifier, temp)
			
			if(senti == 1):
				sentiWord = "<span class = 'positive'> Positive</span>"
				metricAdjust("positive")

			else:
				sentiWord = "<span class = 'negative'> Negative</span>"
				metricAdjust("negative")

			modified = temp + " - " + sentiWord
			simple['text'] = modified
			return json.dumps(simple)
		except:
			pass
   		

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
	


