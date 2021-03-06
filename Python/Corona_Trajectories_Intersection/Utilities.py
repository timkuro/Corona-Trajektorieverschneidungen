# coding=utf-8
import xml.etree.ElementTree as ET
import os, uuid, datetime
from osgeo import osr
from Corona_Trajectories_Intersection.Geometries import *
from config import parameters

def write_kml_to_file(kml, path, filename):
    '''
        Write kml to a file

        :param kml: kml as String
        :param path: target file path
        :param filename: target file name
        :return: path of the saved kml file
    '''

    path = path + "\\" + filename
    datei = open(path, 'a')
    datei.write(kml)
    return path

def read_kml_line(kml):
    '''
    Reads the input kml file and prepares data for further operations

    :param kml: file path to kml file or kml as String
    :return: Track from KML File
    '''

    try:
        os.path.isfile(kml)
        tree = ET.parse(kml)
        root = tree.getroot()
    except:
        root = ET.fromstring(kml)

    if "Track" in root[0][0][1].tag:
        return root[0][0][1]
    else:
        raise Exception('no track-tag found in KML')

def split_line(input_line, personal_id=None):
    '''
    Splits the long line into line sections in a defined timeframe adding the time as attribute

    :param input_line: path to the input
    :personal_id: id of data
    :return: lines in timeframe in a list
    '''
    list_Linestrings = list()

    if personal_id==None:
        personal_id = uuid.uuid4().int

    # define coordinate transformation
    source = osr.SpatialReference()
    source.ImportFromEPSG(parameters['sourceEPSG'])
    target = osr.SpatialReference()
    target.ImportFromEPSG(parameters['targetEPSG'])
    transform_objekt = osr.CoordinateTransformation(source, target)

    # first timestamp
    old_time = (input_line[1].text)
    old_time_py = datetime.datetime.strptime(old_time, '%Y-%m-%dT%H:%M:%SZ')
    # first coordinate
    old_coordinate = (input_line[2].text).split(" ")

    # merge time and coordinate to point
    ogrPoint = ogr.Geometry(ogr.wkbPoint)
    ogrPoint.AddPoint_2D(float(old_coordinate[1]), float(old_coordinate[0]))
    ogrPoint.Transform(transform_objekt)
    old_point = Point(ogrPoint, old_time_py)

    # set starttime and endtime
    if parameters['starttime'] == None or parameters['endtime'] == None:
        starttime = (datetime.datetime.now() - datetime.timedelta(days=14)).strftime('%Y-%m-%dT%H:%M:%SZ')
        endtime = (datetime.datetime.now()).strftime('%Y-%m-%dT%H:%M:%SZ')
    else:
        starttime = parameters['starttime']
        endtime = parameters['endtime']

    startdate_py = datetime.datetime.strptime(starttime, '%Y-%m-%dT%H:%M:%SZ')
    enddate_py = datetime.datetime.strptime(endtime, '%Y-%m-%dT%H:%M:%SZ')

    # loop reads track and splits into sections
    for i in range(3,len(input_line), 2):
        # create attributes vor the point
        time_iso = (input_line[i].text)
        time_py = datetime.datetime.strptime(time_iso, '%Y-%m-%dT%H:%M:%SZ')
        coordinate = (input_line[i+1].text).split(" ")
        ogrPoint = ogr.Geometry(ogr.wkbPoint)
        ogrPoint.AddPoint_2D(float(coordinate[1]), float(coordinate[0]))
        ogrPoint.Transform(transform_objekt)
        point = Point(ogrPoint, time_py)
        # filter points aren't in given time frame
        if (old_point.timestamp > startdate_py) and (point.timestamp < enddate_py):
            distance = ((point.getX()-old_point.getX())**2 + (point.getY()-old_point.getY())**2)**0.5
            time_delta = (point.timestamp-old_point.timestamp).total_seconds()
            # filter outliers (speed > 50 m/s) and lines with a distance over 5000m
            if time_delta > 0 and distance < 5000:
                velocity = distance/time_delta
                if velocity < 50: # [m/s]
                    # fill output list
                    list_Linestrings.append(Linestring(old_point, point, personal_id=personal_id))

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


def boundingBox_intersection(infectedLines, healthyLines):
    '''
    Call Methods to reduce the input datas

    :param infectedLines: input linestrings of the injured person
    :param healthyLines: input other linestrings of the healthy person
    :return: reducedInfectedLines, reducedHealthyLines
    '''

    bboxInfected = create_bounding_box(infectedLines)
    bboxHealthy = create_bounding_box(healthyLines)

    reducedInfectedLines = intersect_bounding_box(infectedLines, bboxHealthy)
    reducedHealthyLines = intersect_bounding_box(healthyLines, bboxInfected)

    return reducedInfectedLines, reducedHealthyLines


def intersect_geom(linestrings_infected, linestrings_healthy):
    '''
    Intersects two lists of linestrings with a defined tolerance by using a Sweep-Status-Structure(SSS)

    :param linestring_infected: input linestrings of the injured person
    :param linestrings_healthy: input other linestrings of the healthy person
    :return: geometric intersection
    '''

    #create result object
    geometric_intersections = list()
    #sweep status structure
    sss = set()
    #create point lists
    ptl_1 = list()
    ptl_2 = list()

    lines_set_infected = set()
    lines_set_healthy = set()

    # each point gets his line
    for line in linestrings_infected:
        if (line.startpoint.getX() < line.endpoint.getX()):
            ptl_1.append([line.startpoint.getX() - parameters['distance'], line])
            ptl_1.append([line.endpoint.getX() + parameters['distance'], line])
        else:
            ptl_1.append([line.startpoint.getX() + parameters['distance'], line])
            ptl_1.append([line.endpoint.getX() - parameters['distance'], line])
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
                            cross_area = trace.intersect_Buffer_line(line)
                            geometric_intersections.append(cross_area)
                        except:
                            continue

                # else: line from sss is from the same set as trace
                else:
                    if line in lines_set_infected:
                        try:
                            cross_area = line.intersect_Buffer_line(trace)
                            geometric_intersections.append(cross_area)
                        except:
                            continue

            sss.add(trace)
    return geometric_intersections

def intersect_time(crossings):
    '''
    checks the temporal intersection of the crossings

    :param crossings: geometric intersections
    :return: temporal intersections
    '''
    temporal_intersections = list()

    for crossing in crossings:
        # calculate time with delta
        line1start = crossing.line1.startpoint.timestamp - datetime.timedelta(minutes=(parameters['timedelta']/2))
        line1end = crossing.line1.endpoint.timestamp + datetime.timedelta(minutes=(parameters['timedelta']/2))
        line2start = crossing.line2.startpoint.timestamp - datetime.timedelta(minutes=(parameters['timedelta']/2))
        line2end = crossing.line2.endpoint.timestamp + datetime.timedelta(minutes=(parameters['timedelta']/2))

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
    srs.ImportFromEPSG(parameters['targetEPSG'])

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
    srs.ImportFromEPSG(parameters['targetEPSG'])

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


if __name__=="__main__":
    pass

