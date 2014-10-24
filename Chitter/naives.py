"""
.. module:: naives
	:platform: Unix, Windows
	:synopsis: The NLTK addon for analyzing Tweet sentiment.
.. moduleauthor:: Kannon Chan <kannon.chan@connect.qut.edu.au>

"""
import nltk
import re
import csv
import random
import os.path
import cPickle as pickle

def simplify(tweet):
    """Simplifies tweet before extraction.

    Args:
        tweet: The text of the tweet to simplify.
    """
    tweet = tweet.lower()
    #urls to URL
    tweet = re.sub('((www\.[^\s]+)|(https?://[^\s]+))','URL',tweet)
    #@username to AT_USER
    tweet = re.sub('@[^\s]+','AT_USER',tweet)    
    #Remove additional white spaces
    tweet = re.sub('[\s]+', ' ', tweet)
    #remove all special characters
    tweet = re.sub('[^a-zA-Z]+',' ',tweet)
    #trim
    tweet = tweet.strip('\'"')
    return tweet


def getStopWordList(stopWordListFileName):
    """Load the stop words list.

    Args:
        stopWordListFileName: The filename of the .txt with the stop words.
    """
    stopWords = []
    stopWords.append('USER_AT')
    stopWords.append('URL')
 
    fp = open(stopWordListFileName, 'r')
    line = fp.readline()
    while line:
        word = line.strip()
        stopWords.append(word)
        line = fp.readline()
    fp.close()
    return stopWords


def replaceDouble(s):
    """Look for 2 or more repetitions of character and replace
    with the character itself

    Args:
        s: The text to analyze.
    """
    pattern = re.compile(r"(.)\1{1,}", re.DOTALL)
    return pattern.sub(r"\1\1", s)
#end

def extractFeatures(tweet):
    """Extract features from the tweet.

    Args:
        tweet: The tweet text to analyze.
    """
    tweet_words = set(tweet)
    features = {}
    for word in featureList:
        features['contains(%s)' % word] = (word in tweet_words)
    return features
#end

#start getfeatureVector
def getFeatureVector(tweet, stopWords):
    """Get features of the tweet.
    Args:
        tweet: The tweet text to analyze.

        stopWords: The list of stop words.
    """
    featureVector = []  
    words = tweet.split()
    for w in words:
        #replace two or more with two occurrences 
        w = replaceDouble(w) 
        #strip punctuation
        w = w.strip('\'"?,.')
        #check if it consists of only words
        val = re.search(r"^[a-zA-Z][a-zA-Z0-9]*[a-zA-Z]+[a-zA-Z0-9]*$", w)
        #ignore if it is a stopWord
        if(w in stopWords or val is None):
            continue
        else:
            featureVector.append(w.lower())
    return featureVector    
#end


def testTweet(classifier,tweet):
    """Using the classifer, take the tweet and determine
    its sentiment.

    Args:
        classifier: What classifier to use.
        tweet: The Tweet text.
    """
    simplifyTestTweet = simplify(tweet)
    sentiment = classifier.classify(extractFeatures(getFeatureVector(simplifyTestTweet, stopWords)))
    return sentiment

def testClassifier(classifier):
    print classifier.show_most_informative_features()

    simplifyTestTweet = 'suck'
    simplifyTestTweet = simplify(simplifyTestTweet)
    sentiment = classifier.classify(extractFeatures(getFeatureVector(simplifyTestTweet, stopWords)))
    print "simplifyTestTweet = %s, sentiment = %s\n" % (simplifyTestTweet, sentiment)

    simplifyTestTweet = 'crap'
    simplifyTestTweet = simplify(simplifyTestTweet)
    sentiment = classifier.classify(extractFeatures(getFeatureVector(simplifyTestTweet, stopWords)))
    print "simplifyTestTweet = %s, sentiment = %s\n" % (simplifyTestTweet, sentiment)

    simplifyTestTweet = 'really bad sad'
    simplifyTestTweet = simplify(simplifyTestTweet)
    sentiment = classifier.classify(extractFeatures(getFeatureVector(simplifyTestTweet, stopWords)))
    print "simplifyTestTweet = %s, sentiment = %s\n" % (simplifyTestTweet, sentiment)


    simplifyTestTweet = 'sucks to be poor'
    simplifyTestTweet = simplify(simplifyTestTweet)
    sentiment = classifier.classify(extractFeatures(getFeatureVector(simplifyTestTweet, stopWords)))
    print "simplifyTestTweet = %s, sentiment = %s\n" % (simplifyTestTweet, sentiment)


    simplifyTestTweet = 'man i am rich abosolutely'
    simplifyTestTweet = simplify(simplifyTestTweet)
    sentiment = classifier.classify(extractFeatures(getFeatureVector(simplifyTestTweet, stopWords)))
    print "simplifyTestTweet = %s, sentiment = %s\n" % (simplifyTestTweet, sentiment)

    simplifyTestTweet = 'Your song is annoying'
    simplifyTestTweet = simplify(simplifyTestTweet)
    sentiment = classifier.classify(extractFeatures(getFeatureVector(simplifyTestTweet, stopWords)))
    print "simplifyTestTweet = %s, sentiment = %s\n" % (simplifyTestTweet, sentiment)

    simplifyTestTweet = 'Larry is my friend'
    simplifyTestTweet = simplify(simplifyTestTweet)
    sentiment = classifier.classify(extractFeatures(getFeatureVector(simplifyTestTweet, stopWords)))
    print "simplifyTestTweet = %s, sentiment = %s\n" % (simplifyTestTweet, sentiment)


csvData = []
pos_tweets = []
neg_tweets = []
featureList = []
tweets = []
stopWords = getStopWordList(os.path.abspath('stopWords.txt'))

pos_train = 10000  
neg_train = 10000
tweet = ''
sentiment = ''


#If there is already trained classifier load it up
if(os.path.isfile('naiveData.pickle')):

    temp = pickle.load(open('naiveData.pickle', 'rb'))
    classifier = temp [1]
    featureList = temp [0]

#Train a new set from database
else:
    #Load Database
    with open('DatasetAll.csv', 'rb') as f:
        reader = csv.reader(f)
        for row in reader:
            csvData.append(row)

    #Shuffle so no repeated results
    random.shuffle(csvData)

    for row in csvData:
        tweet = row[3]
        sentiment = row[1]

        if sentiment == '1' and pos_train > 0:

            pos_tweets.append((tweet,1))
            pos_train -= 1
        else:
            if neg_train > 0:
              neg_tweets.append((tweet,0))
              neg_train -= 1

        if pos_train == 0 and neg_train == 0:
            break
    #Simplify, extract and prepare for training
    for (tweet, sentiment) in pos_tweets + neg_tweets:
        simplifyTweet = simplify(tweet)
        featureVector = getFeatureVector(simplifyTweet, stopWords)
        featureList.extend(featureVector)
        tweets.append((featureVector, sentiment));
    #end loop

    # Duplicates removed from featureList
    featureList = list(set(featureList))

    # Extract features vector for training
    training_set = nltk.classify.util.apply_features(extractFeatures, tweets)

    # Train classifier
    classifier = nltk.NaiveBayesClassifier.train(training_set)

    # need to add accuracy test

    classifier.show_most_informative_features()

    # save_classifier(classifier,extractFeatures,tweets)
    f = open('naiveData.pickle', 'wb')
    pickle.dump([featureList,classifier], f,0)
    f.close()
    testClassifier(classifier)



