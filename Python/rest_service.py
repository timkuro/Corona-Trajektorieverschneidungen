import random
import string
import cherrypy
import os
from Utilities import read_kml_line

lengths = []
trajectories = []
infected_persons = []
test_persons = []

'''https://docs.cherrypy.org/en/3.3.0/tutorial/REST.html#multiple-resources'''

class Infected:

    exposed = True

    def GET(self):
        return infected_persons

    def POST(self):
        rawData = cherrypy.request.body.read(int(cherrypy.request.headers['Content-Length']))
        infected_persons.append(rawData)
        return 'added infected person: \n' + rawData

class Test_person:

    exposed = True

    def GET(self):
         return test_persons

    def POST(self):
        rawData = cherrypy.request.body.read(int(cherrypy.request.headers['Content-Length']))
        test_persons.append(rawData)
        return 'added test person'

if __name__ == '__main__':

    cherrypy.tree.mount(
        Test_person(), '/api/test_person',
        {'/':
            {'request.dispatch': cherrypy.dispatch.MethodDispatcher()}
        }
    )

    cherrypy.engine.start()
    cherrypy.engine.block()