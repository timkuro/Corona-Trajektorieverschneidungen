import random
import string
import cherrypy
import os
from Utilities import read_kml_line

if __name__ == "__main__":
    path_timmy=r"C:\Users\Tim\hs-bochum.de\Christian Koert - GI_Projekt_Wytzisk\Standortverlauf_Juli_2019"
    path_tommy=r"D:\hs-bochum.de\Christian Koert - GI_Projekt_Wytzisk\Standortverlauf_Juli_2019"
    path_kort=r"C:\Users\chris\OneDrive - hs-bochum.de\GI_Projekt_Wytzisk\Standortverlauf_Juli_2019"

    if(os.environ['USERNAME'] == "Thomas"):
        path = path_tommy
    elif(os.environ['USERNAME'] == "Tim"):
        path = path_timmy
    elif(os.environ['USERNAME'] == "chris"):
        path = path_kort

    export_path = path.split("\\")
    trajectories = []

    datei1 = read_kml_line(path[:-len(export_path[-1])] + "Standortverlauf_Juli_2019\Standortverlauf_Christian_Juli2019.kml")
    datei2 = read_kml_line(path[:-len(export_path[-1])] + "Standortverlauf_Juli_2019\Standortverlauf_Thomas_Juli2019.kml")
    datei3 = read_kml_line(path[:-len(export_path[-1])] + "Standortverlauf_Juli_2019\Standortverlauf_Tim_Juli2019.kml")

'''https://docs.cherrypy.org/en/3.3.0/tutorial/REST.html#multiple-resources'''

class Trajectories:

    exposed = True
    trajectories.append(datei1)
    trajectories.append(datei2)

    def GET(self):
         return(f'Here are the lengths of all trajectories: {str(len(trajectories[0]) / 2 - 1)}, {str(len(trajectories[1]) / 2 - 1)}')


    def POST(self, path):
        new_trajectory = read_kml_line(path[:-len(export_path[-1])] + path)
        trajectories.append(new_trajectory)

        return (f'Created a new trajectory with the length: {str(len(trajectories[len(trajectories)-1]) / 2 - 1)}')

if __name__ == '__main__':

    cherrypy.tree.mount(
        Trajectories(), '/api/trajectories',
        {'/':
            {'request.dispatch': cherrypy.dispatch.MethodDispatcher()}
        }
    )

    cherrypy.engine.start()
    cherrypy.engine.block()