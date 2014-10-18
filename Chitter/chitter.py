import os, os.path
import cherrypy
from naives import *
import json
import subprocess
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
from pytagcloud import create_tag_image, create_html_data, make_tags, LAYOUT_HORIZONTAL, LAYOUTS
from pytagcloud.colors import COLOR_SCHEMES
from pytagcloud.lang.counter import get_tag_counts
from string import Template



# OUR TWITTER KEYS
ckey = 'MIoBpZbjBmRfH1ToD5oIuBOEk'
csecret = 'qi37rRfdH3A8EHVCADKsfQJ045MjdYynV1xWAcWk394cIoXoXW'
atoken = '182779783-LNZwsHtGLECvQfhcbD9UtlbjReyLkS7jNHFOiNjD'
asecret = 'XSn95pTAyqhzyfoVhyGdEP6uu5ShbegQ8AGi4zkH5npkg'

#Tweets array
tweets = []
stop = False

#Hahstags
HASHTAGS = ""
html_text = ""


##
# Simple Class for Listening to
# the stream.
##
class listener(StreamListener):

	##
	# When the data is received, and if we're not stopped,
	# get the text and add to the tweets array.
	# Then take the hashtags (if any), and combine into the 
	# global Hashtag string.
	##
    def on_data(self, data):
        global stop, tweets, HASHTAGS
        if stop is False:
            tweet = json.loads(data)            
            tweets.append(tweet['text'])
            try:           
            	hashtags = tweet['entities']['hashtags']
            	for item in hashtags:
            		HASHTAGS += ' ' + item['text']
            except:
            	e = sys.exc_info()[0]
            	print e            		
        else:
            return False

	##
	# Basic error handling.
	##
    def on_error(self, status):
		print status
		#self.disconnect()

# Set up the core features, but don't stream yet.
auth = OAuthHandler(ckey, csecret)
auth.set_access_token(atoken, asecret)

#Global twitter stream
twitterStream = None

##
# The Chitter Web Server
##
class Chitter(object):
    
    ##
    # ENDPOINT: /index.html
    # Load the Index Page.
    ##
    @cherrypy.expose
    def index(self):
        f = open('public/index.html', 'r')
        html = f.read()
        f.close()
        return html
            
    ##
    # ENDPOINT: /prepare
    # Takes a given list of strings, splits it, sanitizes it,
    # and creates a TwitterStreaming object.
    ##        
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
    
    ##
    # ENDPOINT: /stream
    # From the global array of tweets, get the oldest,
    # make a JSON object, acquire the sentiment of the tweet,
    # and return this object to the client.
    ##        
    @cherrypy.expose
    def stream(self):
        global tweets
        try:
            # temporary needs proper variable
            temp = tweets.pop(0)
            simple = {"text":"", "sentiWord":"", "sentiment": 0}
            
            ## GET SENTIMENT ##
            senti = testTweet(classifier, temp)
            simple['text'] = temp
            
            if(senti == 1):
                sentiWord = "<span class = 'positive'> Positive</span>"

            else:
                sentiWord = "<span class = 'negative'> Negative</span>"

            simple['sentiWord'] = sentiWord;
            simple['sentiment'] = senti;
                
            return json.dumps(simple)
        except:
            pass
                    
	##
	# ENDPOINT: /stop
	# Forces the stream to stop, and stops
	# trying to return tweets. Does not 
	# clear the hashtag cloud.
	##                    
    @cherrypy.expose
    def stop(self):
        global twitterStream, tweets, stop
        stop = True	
        twitterStream.disconnect()
        tweets = []

	##
	# ENDPOINT: /clear
	# Same as /stop, but also clears the hashtags
	##        
    @cherrypy.expose
    def clear(self):
    	global twitterStream, tweets, stop, HASHTAGS
        stop = True	
        twitterStream.disconnect()
        tweets = []
    	HASHTAGS = ""

	##
	# ENDPOINT: /cloud
	# Generates a new cloud tag in HTML format,
	# and returns this HTML string.
	##	
    @cherrypy.expose
    def cloud(self):
	global HASHTAGS,html_text

        if len(HASHTAGS)>0:
                if len(get_tag_counts(HASHTAGS)) <= 50 :
                	tags = make_tags(get_tag_counts(HASHTAGS), minsize=30,  maxsize=80, colors=COLOR_SCHEMES['goldfish'])
                	data = create_html_data(tags, (400,400), layout=LAYOUT_HORIZONTAL, fontname='Cantarell')



                	template_file = open(os.path.join('public', 'template.html'), 'r')
                	html_template = Template(template_file.read())

                	context = {}
                	tags_template = '<li class="cnt" style="top: %(top)dpx; left: %(left)dpx; height: %(height)dpx;"><a class="tag %(cls)s" href="#" data-hashtag="%(tag)s" style="top: %(top)dpx;left: %(left)dpx; font-size: %(size)dpx; height: %(height)dpx; line-height:%(lh)dpx;">%(tag)s</a></li>'

                	context['tags'] = ''.join([tags_template % link for link in data['links']])
                	context['width'] = 400
                	context['height'] = 400
                	context['css'] = "".join("a.%(cname)s{color:%(normal)s;}\
                	a.%(cname)s:hover{color:%(hover)s;}" %
                							{'cname':k,
                							'normal': v[0],
                							'hover': v[1]}
                						for k,v in data['css'].items())

                	html_text = html_template.substitute(context)
                        return html_text
                
        	if len(get_tag_counts(HASHTAGS)) > 50 :
                        HASHTAGS = ""
                        return html_text
##
# Standard setup for the simple web server.
#
# Sets the static folders under the /public route.
# Uncomment the line below to enable hosting on AWS or cloud.
##
if __name__ == '__main__':

    conf = {
            '/': {
                'tools.sessions.on': True,
                'tools.staticdir.root': os.path.abspath(os.getcwd()),
                'server.thread_pool':30
             },
             '/static': {
                 'tools.staticdir.on': True,
                 'tools.staticdir.dir': './public'
     }
    }
    #cherrypy.config.update({'server.socket_host': '0.0.0.0','server.socket_port': 3000})
    cherrypy.quickstart(Chitter(), '/', conf)
	


