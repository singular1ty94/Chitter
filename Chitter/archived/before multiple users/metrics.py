import os.path
import cPickle as pickle
import csv
import sys

#set the db
metrics = {}

##
# Adds to the DB
def metricAdjust(k):
	global metrics
	
	if k not in metrics:
		metrics[k] = 1
	else:
		metrics[k] += 1
	
##
# save the file.	
def saveMetrics():
	global metrics
	f = open('metrics.pickle', 'wb')
	pickle.dump(metrics, f, 0)
	f.close()

	with open('public/metrics.csv', 'wb') as csvfile:
		writ = csv.writer(csvfile, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL)
		writ.writerow(('Type', 'Count'))
		
		for key in metrics:
			r = (key, metrics[key])
			writ.writerow(r)

#If there is already stats, grab it
if(os.path.isfile('metrics.pickle')):
    metrics = pickle.load(open('metrics.pickle', 'rb'))
