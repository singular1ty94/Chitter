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

		#sends all tweets to client
		return json.dumps(tweetsREST)

	
	# client will send tweet to get sentiment value
	@cherrypy.expose
   	def streamREST(self,text=""):		
		## GET SENTIMENT ##
		senti = testTweet(classifier, text)
		
		if(senti == 1):
			metricAdjust("positive")
			return json.dumps(1)

		else:
			metricAdjust("negative")
			return json.dumps(0)

		
		# except:
		# 	pass
   		

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
	


