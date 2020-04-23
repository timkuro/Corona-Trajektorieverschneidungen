import xml.etree.ElementTree as ET
import os, sys
from time import strptime, mktime

from Geometries import *

# reads the kml file and prepares data for further operations
def read_kml_line(path):
    tree = ET.parse(path)
    root = tree.getroot()
    if "Track" in root[0][0][1].tag:
        return root[0][0][1]
    else:
        raise Exception('no track-tag found in KML')

def split_line(input_line, startdate_iso, enddate_iso):
    list_Linestrings = list()

    # first timestamp
    old_time = (input_line[1].text)
    old_time_py = mktime(strptime(old_time, '%Y-%m-%dT%H:%M:%SZ'))
    # first coordinate
    old_coordinate = (input_line[2].text).split(" ")
    # merge time and coordinate to point
    old_point = Point(old_coordinate[0], old_coordinate[1], old_time_py)

    startdate_py = mktime(strptime(startdate_iso, '%Y-%m-%dT%H:%M:%SZ'))
    enddate_py = mktime(strptime(enddate_iso, '%Y-%m-%dT%H:%M:%SZ'))

    for i in range(3,len(input_line), 2):
        '''print(i)
        print(str(input_line[i].text) + " " + str(input_line[i+1].text))'''
        time_iso = (input_line[i].text)
        time_py = mktime(strptime(time_iso, '%Y-%m-%dT%H:%M:%SZ'))
        coordinate = (input_line[i+1].text).split(" ")
        point = Point(coordinate[0], coordinate[1], time_py)

        if (old_point.timestamp > startdate_py) and (point.timestamp < enddate_py):
            list_Linestrings.append(Linestring(old_point, point))

        old_point = point

    '''print (list_Linestrings)
    for row in list_Linestrings:
        print(row)'''
    return list_Linestrings

def convert_to_kml(linestrings):
    pass

def intersect_geom(linestring_1, linestring_2):
    #Vorbereitungen
    #Ergebnisobjekt bilden
    result = list();
    #Sweep - Status - Struktur
    # sss anlegen
    sss = set()
    #Punktliste anlegen
    ptl_1 = list()
    ptl_2 = list()

    lines_set_1 = set()
    lines_set_2 = set()

    # Jeder Punkt bekommt seine Linien zugewiesen
    for line in linestring_1:
        ptl_1.append([line.startpoint, line])
        ptl_1.append([line.endpoint, line])
        lines_set_1.add(line)
    print(linestring_2)
    # Jeder Punkt bekommt seine Linien zugewiesen
    for line in linestring_2:
        ptl_2.append([line.startpoint, line])
        ptl_2.append([line.endpoint, line])
        lines_set_2.add(line)

    ptl_gesamt = ptl_1.extend(ptl_2)
    ptl_sorted = sorted(ptl_1, key=lambda list_element: list_element[0].x)

    # Sortierung nach der x-Komponente
    # ptl_1 = sorted(ptl_1, key=lambda list_element: list_element[0].x)
    # ptl_2 = sorted(ptl_2, key=lambda list_element: list_element[0].x)

    # Nur Ausgabe
    for point in ptl_sorted:
        print(point[0])

    # Jeder Punkt der sortierten Punktliste wird durchlaufen
    for point in ptl_sorted:
        # Hole vom ersten Punkt die zugehörige Linie (= trace)
        trace = point[1]
        if trace in sss:
            sss.remove(trace)
        else:
            for line in sss:
                cross_area = None
                # Ermitteln ob Schnittpunkt vorhanden ist
                if trace in lines_set_1:
                    if line in lines_set_2:
                        try:
                            cross_area = trace.intersect_Buffer(line)
                            result.add(cross_area)
                        except:
                            continue
                    #else: "Linie aus SSS ist aus der gleichen Menge wie Trace")
                else:
                    if line in lines_set_1:
                        try:
                            cross_area = trace.intersect_Buffer(line)
                            result.add(cross_area)
                        except:
                            continue
            sss.add(trace)
    print(result)
    return result



def intersect_time(crosspoints):
    pass

path_timmy=r"D:\Uni-Lokal\GI-Projekt Corona\hs-bochum.de\Christian Koert - GI_Projekt_Wytzisk\Standortverlauf_Tim_Juli2019.kml"
path_tommy=r"C:\Users\Thomas\hs-bochum.de\Christian Koert - GI_Projekt_Wytzisk\Standortverlauf_Tim_Juli2019.kml"
path_kort=r"C:\Users\chris\OneDrive - hs-bochum.de\GI_Projekt_Wytzisk\Standortverlauf_Christian_Juli2019.kml"

if(os.environ['USERNAME'] == "Thomas"):
    path = path_tommy
elif(os.environ['USERNAME'] == "Tim"):
    path = path_timmy
elif(os.environ['USERNAME'] == "chris"):
    path = path_kort

print(read_kml_line(path))
lines1 = split_line(read_kml_line(path), '2019-07-01T00:00:00Z', '2019-07-10T00:00:00Z')
print(lines1)
lines2 = split_line(read_kml_line(path), '2019-07-01T00:00:00Z', '2019-07-10T00:00:00Z')
print(lines2)
#intersect_geom(lines1, lines2)