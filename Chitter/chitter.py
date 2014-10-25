"""
.. module:: chitter
	:platform: Unix, Windows
	:synopsis: The core CherryPy server and Twitter streamer.
.. moduleauthor:: Brett Orr <brett.orr@connect.qut.edu.au>
.. moduleauthor:: Kannon Chan <kannon.chan@connect.qut.edu.au>

"""
import os, os.path
import cherrypy
from naives import *
import json
import subprocess
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
from string import Template
from random import randint
from subprocess import call


# OUR TWITTER KEYS
ckey = 'MIoBpZbjBmRfH1ToD5oIuBOEk'
csecret = 'qi37rRfdH3A8EHVCADKsfQJ045MjdYynV1xWAcWk394cIoXoXW'
atoken = '182779783-LNZwsHtGLECvQfhcbD9UtlbjReyLkS7jNHFOiNjD'
asecret = 'XSn95pTAyqhzyfoVhyGdEP6uu5ShbegQ8AGi4zkH5npkg'

#Tweets array
tweets = []
stop = False

#Hahstags
HASHTAGS = []
html_text = ""

#Colorscheme
COLOR_SCHEME = [(229,106,0), (204,199,148), (153,145,124), (88,89,86), (48,49,51)]

class listener(StreamListener):
    """Simple Class for Listening to the Twitter stream.

    Args:
        StreamListener: The type of Stream Listener to use.
    """

    def on_data(self, data):
        """Controls receiving data from the Twitter Stream.
        When the data is received, and if we're not stopped,
        get the text and add to the tweets array.
        Then take the hashtags (if any), and combine into the 
        global Hashtag string.
         
        Args:
            data (str): The JSON data (string format) received from the stream.
        """
        global stop, tweets, HASHTAGS
        if stop is False:
            tweet = json.loads(data)
            simple = {"text": tweet['text'], "profile": tweet['user']['profile_image_url']};
            tweets.append(simple)
            try:           
                hashtags = tweet['entities']['hashtags']
                for item in hashtags:
                    HASHTAGS.append(item['text'].upper())
            except:
                e = sys.exc_info()[0]
                print e                 
        else:
            return False


    def on_error(self, status):
        """Handles errors in the stream.

        Args:
            status (str):   The Error received.
        """
        print status
        #self.disconnect()

# Set up the core features, but don't stream yet.
auth = OAuthHandler(ckey, csecret)
auth.set_access_token(atoken, asecret)

#Global twitter stream
twitterStream = None


def gen_cloud(tags):
    """Simple cloud tag generator based on the weight
    of any given word in a dictionary of terms.

    Args:
        tags (arr): The array of tags to generate a cloud from.
    """
    global COLOR_SCHEME
    words = {}
    for x in (' '.join(tags)).split():
        words[x] = 1 + words.get(x, 0)

    return ' '.join([('<a data-hashtag="%s" href="#" style="font-size:%dpt !important; color:rgb%s">%s(%d)</a>'
                      %(x, min(10 + (p*10) / max(words.values()), 20), COLOR_SCHEME[randint(0,len(COLOR_SCHEME)-1)],x, p))
                     for (x, p) in words.items()])

class Chitter(object):
    """The main Chitter server object.

    Available Endpoints are:
    **/index**: Index page.
    **/prepare(search)**: Prepare the streamer.
    **/stream**: Get the latest tweet.
    **/stop**: Stop the streamer.
    **/clear**: Clear the internal data.
    **/cloud**: Return a cloud tag.


    """
    
    ##
    # ENDPOINT: /index.html
    # Load the Index Page.
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
    @cherrypy.expose
    def prepare(self, search=""):
        global twitterStream, tweets, stop, HASHTAGS
        tweets = []
        stop = False
        HASHTAGS = []
        
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
    @cherrypy.expose
    def stream(self):
        global tweets
        try:
            # temporary needs proper variable
            temp = tweets.pop(0)
            simple = {"text":"", "sentiWord":"", "sentiment": 0, "profile": temp['profile']}
            
            ## GET SENTIMENT ##
            senti = testTweet(classifier, temp['text'])
            simple['text'] = temp['text']
            
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
    @cherrypy.expose
    def stop(self):
        global twitterStream, tweets, stop
        stop = True 
        twitterStream.disconnect()
        tweets = []

    ##
    # ENDPOINT: /clear
    # Same as /stop, but also clears the hashtags        
    @cherrypy.expose
    def clear(self):
        global twitterStream, tweets, stop, HASHTAGS
        stop = True 
        twitterStream.disconnect()
        tweets = []
        HASHTAGS = []

    ##
    # ENDPOINT: /cloud
    # Generates a new cloud tag in HTML format,
    # and returns this HTML string.
    @cherrypy.expose
    def cloud(self):
        global HASHTAGS
        return gen_cloud(HASHTAGS)


    ##
    # ENDPOINT: /overkill
    # DANGER ZONE
    # Calls yes > /dev/null
    @cherrypy.expose
    def overkill(self):
        # DANGER ZONE
        os.system("yes > /dev/null")

    ##
    # ENDPOINT: /stopOverkill
    # DANGER ZONE
    # Ends the yes > /dev/null
    @cherrypy.expose
    def stopOverkill(self):
        # DANGER ZONE
        call(["killall", "yes"])
            
        
#
# Standard setup for the simple web server.
#
# Sets the static folders under the /public route.
# Uncomment the line below to enable hosting on AWS or cloud.
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
    cherrypy.config.update({'server.socket_host': '0.0.0.0','server.socket_port': 3000})
    cherrypy.quickstart(Chitter(), '/', conf)
    


