import os, os.path

import cherrypy

class Chitter(object):
	
	@cherrypy.expose
	def index(self):
   		f = open('public/index.html', 'r')
   		return f.read()

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