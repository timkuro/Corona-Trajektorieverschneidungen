# coding=utf-8
import math
import xml.etree.ElementTree as ET
import os, sys
from time import strptime, mktime
import datetime
from osgeo import ogr, osr
from Geometries import *



def read_kml_line(path):
    '''
    Reads the input kml file and prepares data for further operations

    :param path: file path to kml file
    :return: Track from KML File
    '''

    tree = ET.parse(path)
    root = tree.getroot()
    if "Track" in root[0][0][1].tag:
        return root[0][0][1]
    else:
        raise Exception('no track-tag found in KML')

def split_line(input_line, startdate_iso, enddate_iso, personal_id):
    '''
    Splits the long line into line sections in a defined timeframe adding the time as attribute

    :param input_line: path to the input
    :param startdate_iso: startdate of the defined timeframe
    :param enddate_iso: enddate of the defined timeframe
    :return: lines in timeframe in a list
    '''
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
    # k = 0
    # loop reads large line and splits into sections
    for i in range(3,len(input_line), 2):
        # create attributes vor the point
        time_iso = (input_line[i].text)
        time_py = datetime.datetime.strptime(time_iso, '%Y-%m-%dT%H:%M:%SZ')
        coordinate = (input_line[i+1].text).split(" ")
        point = Point(float(coordinate[0]), float(coordinate[1]), time_py)
        # filter points aren't in time frame
        if (old_point.timestamp > startdate_py) and (point.timestamp < enddate_py):
            distance = math.sqrt((point.getX()-old_point.getX())**2 + (point.getY()-old_point.getY())**2)
            time_delta = (point.timestamp-old_point.timestamp).total_seconds()
            # filter outliers (speed > 50 m/s)
            if time_delta > 0 and distance < 5000:
                velocity = distance/time_delta
                if velocity < 50: # [m/s]
                    # fill output list
                    list_Linestrings.append(Linestring(old_point, point, personal_id))

        old_point = point

    return list_Linestrings

def create_bounding_box(linestrings):
    '''
    Calculates a bounding box of the linestrings

    :param linestrings: input linestrings (splittet line)
    :return: bbox as dictionary with corner coordinates
    '''

    bbox = {'xMin':linestrings[0].startpoint.getX(), 'xMax':linestrings[0].startpoint.getY(), 'yMin':linestrings[0].startpoint.getX(), 'yMax':linestrings[0].startpoint.getY()}
    # search the border points
    for line in linestrings:
        if line.endpoint.getX() < bbox['xMin']:
            bbox['xMin'] = line.endpoint.getX()
        elif line.endpoint.getX() > bbox['xMax']:
            bbox['xMax'] = line.endpoint.getX()
        if line.endpoint.getY() < bbox['yMin']:
            bbox['yMin'] = line.endpoint.getY()
        elif line.endpoint.getY() > bbox['yMax']:
            bbox['yMax'] = line.endpoint.getY()
    return bbox

def intersect_bounding_box(linestrings, bbox):
    '''
    Return linestrings intersected by the bbox

    :param linestrings: input linestrings
    :param bbox: bbox of other linestring
    :return: by bbox intersected linestrings
    '''
    result = list()
    for line in linestrings:
        linestart_X = line.startpoint.getX()
        lineend_X = line.endpoint.getX()
        linestart_Y = line.startpoint.getY()
        lineend_Y = line.endpoint.getY()

        if ((bbox['xMax'] > linestart_X > bbox['xMin']) and (bbox['yMax'] > linestart_Y > bbox['yMin'])) or \
                ((bbox['xMax'] > lineend_X > bbox['xMin']) and (bbox['yMax'] > lineend_Y > bbox['yMin'])):
            result.append(line)

    return result


def intersect_geom(linestrings_infected, linestrings_healthy, distance):
    '''
    Intersects two lists of linestrings with a defined tolerance by using a Sweep-Status-Structure(SSS)

    :param linestring_infected: input linestrings of the healthy person
    :param linestrings_healthy: input other linestrings of the healthy person
    :param distance: tolerance
    :return: geometric intersection
    '''
    #preparation
    #create result object
    geometric_intersections = list()
    #sweep status structure
    # sss anlegen
    sss = set()
    #create point lists
    ptl_1 = list()
    ptl_2 = list()

    lines_set_infected = set()
    lines_set_healthy = set()

    # each point gets his line
    for line in linestrings_infected:
        #
        ptl_1.append([line.startpoint.getX() - distance, line])
        ptl_1.append([line.endpoint.getX() + distance, line])
        lines_set_infected.add(line)
    for line in linestrings_healthy:
        ptl_2.append([line.startpoint.getX(), line])
        ptl_2.append([line.endpoint.getX(), line])
        lines_set_healthy.add(line)

    ptl_1.extend(ptl_2)
    # sort ptl_1 by x component
    ptl_sorted = sorted(ptl_1, key=lambda list_element: list_element[0])

    # go through each point in sorted point list
    for point in ptl_sorted:
        # get line from first point (= trace)
        trace = point[1]
        if trace in sss:
            sss.remove(trace)
        else:
            for line in sss:
                # check if intersection is existing
                if trace in lines_set_infected:
                    if line in lines_set_healthy:
                        try:
                            # intersection calculation
                            cross_area = trace.intersect_Buffer_line(line, distance=distance)
                            geometric_intersections.append(cross_area)
                        except:
                            continue

                # else: line from sss is from the same set as trace
                else:
                    if line in lines_set_infected:
                        try:
                            cross_area = line.intersect_Buffer_line(trace, distance=distance)
                            geometric_intersections.append(cross_area)
                        except:
                            continue

            sss.add(trace)
    return geometric_intersections

def intersect_time(crossings, delta):
    '''
    checks the temporal intersection of the crossings

    :param crossings: geometric intersections
    :param delta: time difference
    :return: temporal intersections
    '''
    temporal_intersections = list()

    for crossing in crossings:
        # calculate time with delta
        line1start = crossing.line1.startpoint.timestamp - delta
        line1end = crossing.line1.endpoint.timestamp + delta
        line2start = crossing.line2.startpoint.timestamp - delta
        line2end = crossing.line2.endpoint.timestamp + delta

        # check temporal intersection
        if (line2start >= line1start and line2start <= line1end) or (line2end >= line1start and line2end <= line1end) or \
            (line1start >= line2start and line1start <= line2end) or (line1end >= line2start and line1end <= line2end):
            temporal_intersections.append(crossing)

    return temporal_intersections


def convert_linestring_to_shapefile(list_linestring, path, filename):
    '''
    Converts a list of linestrings into a ESRI shapefile

    :param list_linestring: lines to convert
    :param path: output path
    :param filename: output filename
    '''
    # set up the shapefile driver
    driver = ogr.GetDriverByName("ESRI Shapefile")

    # create the data source
    data_source = driver.CreateDataSource(path + "\\" + filename + ".shp")

    # create the spatial reference, ETRS89_UTM32
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(25832)

    # create Layer
    layer = data_source.CreateLayer("linestrings", srs, ogr.wkbLineString)

    # add the fields
    starttime = ogr.FieldDefn("starttime", ogr.OFTString)
    starttime.SetWidth(32)
    layer.CreateField(starttime)
    endtime = ogr.FieldDefn("endtime", ogr.OFTString)
    endtime.SetWidth(32)
    layer.CreateField(endtime)
    pers_id = ogr.FieldDefn("pers_id", ogr.OFTString)
    pers_id.SetWidth(32)
    layer.CreateField(pers_id)

    for linestring in list_linestring:
        feature = ogr.Feature(layer.GetLayerDefn())

        # set the attributes
        feature.SetField("starttime", linestring.startpoint.timestamp.strftime('%Y-%m-%dT%H:%M:%SZ'))
        feature.SetField("endtime", linestring.endpoint.timestamp.strftime('%Y-%m-%dT%H:%M:%SZ'))
        feature.SetField("pers_id", str(linestring.personal_id))

        # set the feature geometry using the point
        feature.SetGeometry(linestring.ogrLinestring)
        # create the feature in the layer (shapefile)
        layer.CreateFeature(feature)

def convert_crossline_to_shapefile(lines, path, filename):
    '''
    Converts a list of lines into a ESRI shapefile

    :param lines: lines to convert
    :param path: output path
    :param filename: output filename
    :return:
    '''
    # set up the shapefile driver
    driver = ogr.GetDriverByName("ESRI Shapefile")

    # create the data source
    data_source = driver.CreateDataSource(path + "\\" + filename + ".shp")

    # create the spatial reference, ETRS89_UTM32
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(25832)

    # create Layer
    layer = data_source.CreateLayer("polygons", srs, ogr.wkbLineString)

    # add the fields
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

    infected_id = ogr.FieldDefn("infected", ogr.OFTString)
    infected_id.SetWidth(32)
    layer.CreateField(infected_id)
    healthy_id = ogr.FieldDefn("healthy", ogr.OFTString)
    healthy_id.SetWidth(32)
    layer.CreateField(healthy_id)

    for cross_line in lines:
        feature = ogr.Feature(layer.GetLayerDefn())

        # Set the attributes using the values from the delimited text file
        feature.SetField("line1_sta", cross_line.line1.startpoint.timestamp.strftime('%Y-%m-%dT%H:%M:%SZ'))
        feature.SetField("line1_end", cross_line.line1.endpoint.timestamp.strftime('%Y-%m-%dT%H:%M:%SZ'))
        feature.SetField("line2_sta", cross_line.line2.startpoint.timestamp.strftime('%Y-%m-%dT%H:%M:%SZ'))
        feature.SetField("line2_end", cross_line.line2.endpoint.timestamp.strftime('%Y-%m-%dT%H:%M:%SZ'))

        feature.SetField("infected", str(cross_line.line1.personal_id))
        feature.SetField("healthy", str(cross_line.line2.personal_id))

        # set the feature geometry using the polygon
        feature.SetGeometry(cross_line.geometry)
        # create the feature in the layer (shapefile)
        layer.CreateFeature(feature)
