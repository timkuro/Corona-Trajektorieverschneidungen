# coding=utf-8
import math
import xml.etree.ElementTree as ET
import os, sys
from time import strptime, mktime
import datetime
from osgeo import ogr, osr
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
    k = 0
    for i in range(3,len(input_line), 2):
        time_iso = (input_line[i].text)
        time_py = datetime.datetime.strptime(time_iso, '%Y-%m-%dT%H:%M:%SZ')
        coordinate = (input_line[i+1].text).split(" ")
        point = Point(float(coordinate[0]), float(coordinate[1]), time_py)
        if (old_point.timestamp > startdate_py) and (point.timestamp < enddate_py):
            distance = (math.sqrt((point.x-old_point.x)**2 + (point.y-old_point.y)**2)/360)*40000000
            time_delta = (point.timestamp-old_point.timestamp).total_seconds()
            if time_delta >0 and distance < 5000:
                velocity = distance/time_delta
                if velocity < 50: # [m/s]
                    list_Linestrings.append(Linestring(old_point, point))
                else:
                    k = k+1
                    #print(f"{k}. Ausreißer")

        old_point = point

    return list_Linestrings





def intersect_geom(linestring_1, linestring_2, distance):
    #Vorbereitungen
    #Ergebnisobjekt bilden
    result = list();
    #Sweep - Status - Struktur
    # sss anlegen
    sss = set()
    #Punktliste anlegen
    ptl_1 = list()
    ptl_2 = list()

    lines_set_infected = set()
    lines_set_healthy = set()

    # Jeder Punkt bekommt seine Linien zugewiesen
    for line in linestring_1:
        ptl_1.append([line.startpoint, line])
        ptl_1.append([line.endpoint, line])
        lines_set_infected.add(line)
    # Jeder Punkt bekommt seine Linien zugewiesen
    for line in linestring_2:
        ptl_2.append([line.startpoint, line])
        ptl_2.append([line.endpoint, line])
        lines_set_healthy.add(line)

    ptl_1.extend(ptl_2)
    ptl_sorted = sorted(ptl_1, key=lambda list_element: list_element[0].x)

    # Sortierung nach der x-Komponente
    # ptl_1 = sorted(ptl_1, key=lambda list_element: list_element[0].x)
    # ptl_2 = sorted(ptl_2, key=lambda list_element: list_element[0].x)

    # Jeder Punkt der sortierten Punktliste wird durchlaufen
    for point in ptl_sorted:
        # Hole vom ersten Punkt die zugehörige Linie (= trace)
        trace = point[1]
        if trace in sss:
            sss.remove(trace)
        else:
            for line in sss:
                # Ermitteln ob Schnittpunkt vorhanden ist
                if trace in lines_set_infected:
                    if line in lines_set_healthy:
                        try:
                            cross_area = trace.intersect_Buffer_line(line, distance=distance)
                            result.append(cross_area)
                        except:
                            continue

                    #else: "Linie aus SSS ist aus der gleichen Menge wie Trace")
                else:
                    if line in lines_set_infected:
                        try:
                            cross_area = line.intersect_Buffer_line(trace, distance=distance)
                            result.append(cross_area)
                        except:
                            continue

            sss.add(trace)
    return result

def intersect_time(crossareas, delta):
    result = list()

    for crossarea in crossareas:
        line1start = crossarea.line1.startpoint.timestamp - delta
        line1end = crossarea.line1.endpoint.timestamp + delta
        line2start = crossarea.line2.startpoint.timestamp - delta
        line2end = crossarea.line2.endpoint.timestamp + delta

        #Pruefe auf zeitliche Ueberschneidung der Intervalle
        if (line2start >= line1start and line2start <= line1end) or (line2end >= line1start and line2end <= line1end) or \
            (line1start >= line2start and line1start <= line2end) or (line1end >= line2start and line1end <= line2end):
            result.append(crossarea)

    return result


def convert_linestring_to_shapefile(list_linestring, path, dataname):
    # set up the shapefile driver
    driver = ogr.GetDriverByName("ESRI Shapefile")

    # create the data source
    data_source = driver.CreateDataSource(path + "\\" + dataname + ".shp")

    # create the spatial reference, WGS84
    '''srs = osr.SpatialReference()
    srs.ImportFromEPSG(4326)'''

    # Create Layer
    layer = data_source.CreateLayer("linestrings", None, ogr.wkbLineString)

    # Add the fields
    starttime = ogr.FieldDefn("starttime", ogr.OFTString)
    starttime.SetWidth(32)
    layer.CreateField(starttime)
    endtime = ogr.FieldDefn("endtime", ogr.OFTString)
    endtime.SetWidth(32)
    layer.CreateField(endtime)

    for linestring in list_linestring:
        feature = ogr.Feature(layer.GetLayerDefn())

        # Set the attributes using the values from the delimited text file
        feature.SetField("starttime", linestring.startpoint.timestamp.strftime('%Y-%m-%dT%H:%M:%SZ'))
        feature.SetField("endtime", linestring.endpoint.timestamp.strftime('%Y-%m-%dT%H:%M:%SZ'))

        # Create geometry from linestring object
        line_ogr = ogr.Geometry(ogr.wkbLineString)
        line_ogr.AddPoint(linestring.startpoint.x, linestring.startpoint.y)
        line_ogr.AddPoint(linestring.endpoint.x, linestring.endpoint.y)

        # Set the feature geometry using the point
        feature.SetGeometry(line_ogr)
        # Create the feature in the layer (shapefile)
        layer.CreateFeature(feature)


    '''if arcpy.Exists(path + "\\" + dataname + ".shp"):
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
            insertCursor.insertRow([polyline, line_start, line_end])'''


def convert_crossarea_to_shapefile(resultList, path, dataname):
    # set up the shapefile driver
    driver = ogr.GetDriverByName("ESRI Shapefile")

    # create the data source
    data_source = driver.CreateDataSource(path + "\\" + dataname + ".shp")

    # create the spatial reference, WGS84
    '''srs = osr.SpatialReference()
    srs.ImportFromEPSG(4326)'''
    # Create Layer
    layer = data_source.CreateLayer("polygons", None, ogr.wkbPolygon)

    # Add the fields
    starttime = ogr.FieldDefn("line1_sta", ogr.OFTString)
    starttime.SetWidth(32)
    layer.CreateField(starttime)
    endtime = ogr.FieldDefn("line1_end", ogr.OFTString)
    endtime.SetWidth(32)
    layer.CreateField(endtime)
    starttime = ogr.FieldDefn("line2_sta", ogr.OFTString)
    starttime.SetWidth(32)
    layer.CreateField(starttime)
    endtime = ogr.FieldDefn("line2_end", ogr.OFTString)
    endtime.SetWidth(32)
    layer.CreateField(endtime)

    for cross_area in resultList:
        feature = ogr.Feature(layer.GetLayerDefn())

        # Set the attributes using the values from the delimited text file
        feature.SetField("line1_sta", cross_area.line1.startpoint.timestamp.strftime('%Y-%m-%dT%H:%M:%SZ'))
        feature.SetField("line1_end", cross_area.line1.endpoint.timestamp.strftime('%Y-%m-%dT%H:%M:%SZ'))
        feature.SetField("line2_sta", cross_area.line2.startpoint.timestamp.strftime('%Y-%m-%dT%H:%M:%SZ'))
        feature.SetField("line2_end", cross_area.line2.endpoint.timestamp.strftime('%Y-%m-%dT%H:%M:%SZ'))

        # Set the feature geometry using the polygon
        feature.SetGeometry(cross_area.polygon)
        # Create the feature in the layer (shapefile)
        layer.CreateFeature(feature)


def convert_crossline_to_shapefile(resultList, path, dataname):
    # set up the shapefile driver
    driver = ogr.GetDriverByName("ESRI Shapefile")

    # create the data source
    data_source = driver.CreateDataSource(path + "\\" + dataname + ".shp")

    # create the spatial reference, WGS84
    '''srs = osr.SpatialReference()
    srs.ImportFromEPSG(4326)'''
    # Create Layer
    layer = data_source.CreateLayer("polygons", None, ogr.wkbLineString)

    # Add the fields
    starttime = ogr.FieldDefn("line1_sta", ogr.OFTString)
    starttime.SetWidth(32)
    layer.CreateField(starttime)
    endtime = ogr.FieldDefn("line1_end", ogr.OFTString)
    endtime.SetWidth(32)
    layer.CreateField(endtime)
    starttime = ogr.FieldDefn("line2_sta", ogr.OFTString)
    starttime.SetWidth(32)
    layer.CreateField(starttime)
    endtime = ogr.FieldDefn("line2_end", ogr.OFTString)
    endtime.SetWidth(32)
    layer.CreateField(endtime)

    for cross_line in resultList:
        feature = ogr.Feature(layer.GetLayerDefn())

        # Set the attributes using the values from the delimited text file
        feature.SetField("line1_sta", cross_line.line1.startpoint.timestamp.strftime('%Y-%m-%dT%H:%M:%SZ'))
        feature.SetField("line1_end", cross_line.line1.endpoint.timestamp.strftime('%Y-%m-%dT%H:%M:%SZ'))
        feature.SetField("line2_sta", cross_line.line2.startpoint.timestamp.strftime('%Y-%m-%dT%H:%M:%SZ'))
        feature.SetField("line2_end", cross_line.line2.endpoint.timestamp.strftime('%Y-%m-%dT%H:%M:%SZ'))

        # Set the feature geometry using the polygon
        feature.SetGeometry(cross_line.geometry)
        # Create the feature in the layer (shapefile)
        layer.CreateFeature(feature)
