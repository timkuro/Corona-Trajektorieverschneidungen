import time

import cherrypy
from Utilities import *
import os

infected_persons = []
test_persons = []

class Infected_person:
    exposed = True

    def GET(self):
        return str(len(infected_persons))

    def POST(self):
        rawData = cherrypy.request.body.read(int(cherrypy.request.headers['Content-Length']))
        rawData_xml = read_kml_line(rawData)

        i = (len)(infected_persons) + 1
        splitted_lines = split_line(rawData_xml, '2019-07-01T00:00:00Z', '2019-08-01T00:00:00Z', (str(i)))
        infected_persons.append(splitted_lines)
        return splitted_lines.__str__()


class Test_person:
    exposed = True

    def GET(self):
        return str(len(test_persons))

    def POST(self):
        starttime = time.time()
        rawData = cherrypy.request.body.read(int(cherrypy.request.headers['Content-Length']))
        rawData_xml = read_kml_line(rawData)

        i = (len)(infected_persons) + 1
        splitted_lines = split_line(rawData_xml, '2019-07-01T00:00:00Z', '2019-08-01T00:00:00Z', (str(i)))
        test_persons.append(splitted_lines)

        infectedLines = []
        for element in infected_persons:
            infectedLines += element
        healthyLines = splitted_lines

        infectedLines, healthyLines = boundingBox_intersection(infectedLines, healthyLines)

        result_geom = intersect_geom(infectedLines, healthyLines, distance=10)
        result_time = intersect_time(result_geom, delta=datetime.timedelta(minutes=15))

        convert_crossline_to_shapefile(result_time, "C:\\Users\\" + os.environ['USERNAME'] + "\\", "corona_contacts")
        endtime = time.time()
        timedif = endtime - starttime
        return f"You may mave had {len(result_time)} contacts with infected persons. To see the positions, open " \
               f"C:\\Users\\" + os.environ['USERNAME'] + "\\", "corona_contacts.shp. \nPost took " + (str)(timedif) + " seconds."


if __name__ == '__main__':
    cherrypy.tree.mount(
        Test_person(), '/api/test_person',
        {'/':
             {'request.dispatch': cherrypy.dispatch.MethodDispatcher()}
         }
    )
    cherrypy.tree.mount(
        Infected_person(), '/api/infected_person',
        {'/':
             {'request.dispatch': cherrypy.dispatch.MethodDispatcher()}
         })

    cherrypy.engine.start()
    cherrypy.engine.block()
