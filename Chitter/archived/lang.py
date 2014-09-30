import langid
import os.path
import cPickle as pickle
import json
import csv
import sys

#set the db
lang_d = {}

##
# Identifies the language of the tweet
# and adds it to the db.
def identify(text):
	global lang_d
	
	x = langid.classify(text);
	
	if x[0] not in lang_d:
		lang_d[x[0]] = 1
	else:
		lang_d[x[0]] += 1
	
##
# save the file.	
def save():
	global lang_d
	f = open('lang.pickle', 'wb')
	pickle.dump(lang_d, f, 0)
	f.close()

	with open('public/lang.csv', 'wb') as csvfile:
		writ = csv.writer(csvfile, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL)
		writ.writerow(('Language', 'Count'))
		
		for key in lang_d:
			r = (key, lang_d[key])
			writ.writerow(r)
		
def test():
	identify("This should be english.")
	identify("Je suis un femm grande.")
	identify("Mucho gracias amigo")
	identify("A second english sentence.")
	save()


#If there is already stats, grab it
if(os.path.isfile('lang.pickle')):
    lang_d = pickle.load(open('lang.pickle', 'rb'))

for arg in sys.argv:
	identify(arg)
save()
    
	 
		


