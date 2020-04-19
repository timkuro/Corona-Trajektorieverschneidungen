import xml.etree.ElementTree as ET
import os, sys

from Geometries import *

# reads the kml file and prepares data for further operations
def read_kml_line(path):
    tree = ET.parse(path)
    root = tree.getroot()
    if "Track" in root[0][0][1].tag:
        return root[0][0][1]
    else:
        raise Exception('no track-tag found in KML')

def split_line(input_line):
    list_Linestrings = list()

    old_time = (input_line[1].text)
    old_coordinate = (input_line[2].text).split(" ")
    old_point = Point(old_coordinate[0], old_coordinate[1], old_time)

    for i in range(3,len(input_line), 2):
        '''print(i)
        print(str(input_line[i].text) + " " + str(input_line[i+1].text))'''

        time = (input_line[i].text)
        coordinate = (input_line[i+1].text).split(" ")
        point = Point(coordinate[0], coordinate[1], time)

        list_Linestrings.append(Linestring(old_point, point))

        old_point = point

    '''print (list_Linestrings)
    for row in list_Linestrings:
        print(row)'''
    return list_Linestrings

def convert_to_kml(linestrings):
    pass

def intersect_geom(linestrings):
    pass

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
split_line(read_kml_line(path))