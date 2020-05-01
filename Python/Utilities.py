# coding=utf-8

import xml.etree.ElementTree as ET
import os, sys
from time import strptime, mktime
import datetime
from osgeo import ogr
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
    old_time_py = datetime.datetime.strptime(old_time, '%Y-%m-%dT%H:%M:%SZ')
    # first coordinate
    old_coordinate = (input_line[2].text).split(" ")
    # merge time and coordinate to point
    old_point = Point(float(old_coordinate[0]), float(old_coordinate[1]), old_time_py)

    startdate_py = datetime.datetime.strptime(startdate_iso, '%Y-%m-%dT%H:%M:%SZ')
    enddate_py = datetime.datetime.strptime(enddate_iso, '%Y-%m-%dT%H:%M:%SZ')

    for i in range(3,len(input_line), 2):
        '''print(i)
        print(str(input_line[i].text) + " " + str(input_line[i+1].text))'''
        time_iso = (input_line[i].text)
        time_py = datetime.datetime.strptime(time_iso, '%Y-%m-%dT%H:%M:%SZ')
        coordinate = (input_line[i+1].text).split(" ")
        point = Point(float(coordinate[0]), float(coordinate[1]), time_py)

        if (old_point.timestamp > startdate_py) and (point.timestamp < enddate_py):
            list_Linestrings.append(Linestring(old_point, point))

        old_point = point

    '''print (list_Linestrings)
    for row in list_Linestrings:
        print(row)'''
    return list_Linestrings

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
    # Jeder Punkt bekommt seine Linien zugewiesen
    for line in linestring_2:
        ptl_2.append([line.startpoint, line])
        ptl_2.append([line.endpoint, line])
        lines_set_2.add(line)

    ptl_1.extend(ptl_2)
    ptl_sorted = sorted(ptl_1, key=lambda list_element: list_element[0].x)

    # Sortierung nach der x-Komponente
    # ptl_1 = sorted(ptl_1, key=lambda list_element: list_element[0].x)
    # ptl_2 = sorted(ptl_2, key=lambda list_element: list_element[0].x)

    '''# Nur Ausgabe
    for point in ptl_sorted:
        print(point[0])'''

    # Jeder Punkt der sortierten Punktliste wird durchlaufen
    for point in ptl_sorted:
        # Hole vom ersten Punkt die zugehörige Linie (= trace)
        trace = point[1]
        if trace in sss:
            sss.remove(trace)
        else:
            for line in sss:
                # Ermitteln ob Schnittpunkt vorhanden ist
                if trace in lines_set_1:
                    if line in lines_set_2:
                        try:
                            cross_area = trace.intersect_Buffer(line)
                            result.append(cross_area)
                        except:
                            continue

                    #else: "Linie aus SSS ist aus der gleichen Menge wie Trace")
                else:
                    if line in lines_set_1:
                        try:
                            cross_area = trace.intersect_Buffer(line)
                            result.append(cross_area)
                        except:
                            continue

            sss.add(trace)
    return result

def intersect_time(crossareas):
    result = list()

    for crossarea in crossareas:
        line1start = crossarea.line1.startpoint.timestamp
        line1end = crossarea.line1.endpoint.timestamp
        line2start = crossarea.line2.startpoint.timestamp
        line2end = crossarea.line2.endpoint.timestamp

        #Pruefe auf zeitliche Ueberschneidung der Intervalle
        if (line2start >= line1start and line2start <= line1end) or (line2end >= line1start and line2end <= line1end) or \
            (line1start >= line2start and line1start <= line2end) or (line1end >= line2start and line1end <= line2end):
            result.append(crossarea)

    return result


'''
def convert_linestring_to_shapefile(list_linestring, path, dataname):
    if arcpy.Exists(path + "\\" + dataname + ".shp"):
        arcpy.management.Delete(path + "\\" + dataname + ".shp")
    arcpy.management.CreateFeatureclass(path, dataname + ".shp", "Polyline")
    arcpy.management.AddField(path + "\\" + dataname + ".shp", "starttime", "TEXT")
    arcpy.management.AddField(path + "\\" + dataname + ".shp", "endtime", "TEXT")

    with arcpy.da.InsertCursor(path + "\\" + dataname + ".shp", ["SHAPE@", "starttime", "endtime"]) as insertCursor:
        for linestring in list_linestring:
            line_start = str(linestring.startpoint.timestamp)
            line_end = str(linestring.endpoint.timestamp)
            polyline = arcpy.Polyline(arcpy.Array([arcpy.Point(linestring.startpoint.x, linestring.startpoint.y), arcpy.Point(linestring.endpoint.x, linestring.endpoint.y)]), arcpy.SpatialReference(4326))
            print(polyline.length)
            insertCursor.insertRow([polyline, line_start, line_end])
'''
'''
def convert_crossarea_to_shapefile(resultList, path, dataname):
    if arcpy.Exists(path + "\\" + dataname + ".shp"):
        arcpy.management.Delete(path + "\\" + dataname + ".shp")
    arcpy.management.CreateFeatureclass(path, dataname + ".shp", "Polygon")
    arcpy.management.AddField(path + "\\" + dataname + ".shp", "line1_sta", "TEXT")
    arcpy.management.AddField(path + "\\" + dataname + ".shp", "line1_end", "TEXT")
    arcpy.management.AddField(path + "\\" + dataname + ".shp", "line2_sta", "TEXT")
    arcpy.management.AddField(path + "\\" + dataname + ".shp", "line2_end", "TEXT")

    with arcpy.da.InsertCursor(path + "\\" + dataname + ".shp", ["SHAPE@", "line1_sta", "line1_end", "line2_sta", "line2_end"]) as insertCursor:
        for cross_area in resultList:
            line1_start = cross_area.line1.startpoint.timestamp
            line1_end = cross_area.line1.endpoint.timestamp
            line2_start = cross_area.line2.startpoint.timestamp
            line2_end = cross_area.line2.endpoint.timestamp
            insertCursor.insertRow([cross_area.polygon, line1_start, line1_end, line2_start, line2_end])
'''


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

    lines1 = split_line(read_kml_line(path[:-len(export_path[-1])] + "Standortverlauf_Juli_2019\Standortverlauf_Tim_Juli2019.kml"), '2019-07-01T00:00:00Z', '2019-07-02T00:00:00Z')
    #convert_linestring_to_shapefile(lines1, path[:-len(export_path[-1])] + r"Ergebnisse\Splitted_Lines", "Splitted_Lines_Tim_Juli2019")
    print(lines1)

    lines2 = split_line(read_kml_line(path[:-len(export_path[-1])] + "Standortverlauf_Juli_2019\Standortverlauf_Christian_Juli2019.kml"), '2019-07-01T00:00:00Z', '2019-07-02T00:00:00Z')
    #convert_linestring_to_shapefile(lines2, path[:-len(export_path[-1])] + r"Ergebnisse\Splitted_Lines", "Splitted_Lines_Christian_Juli2019")
    print(lines2)

    result_geom = intersect_geom(lines1, lines2)

    result_time = intersect_time(result_geom)

    #convert_crossarea_to_shapefile(result_time, path[:-len(export_path[-1])] + r"Ergebnisse\Schnitt_Zeitlich", "time_intersection_tim_christian")