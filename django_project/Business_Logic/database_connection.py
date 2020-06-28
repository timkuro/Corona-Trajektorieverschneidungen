from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.geos import Point as geosPoint
from osgeo import ogr

from Business_Logic.Geometries import Point, Linestring
from Business_Logic.Utilities import *
from application1.models import Point as Models_Point, Line_String as Models_Line_String
from config import parameters


def write_in_database(list_linestring):
    '''
    Writing a every element of the list of linestring (following the schema of the business logic) in a database
    :param list_linestring: a list of Geometries.Linestring objects
    '''
    for linestring in list_linestring:
        already_existing = [0, 0]
        try:
            models_point_start = Models_Point.objects.get(x=linestring.startpoint.getX(), y=linestring.startpoint.getY(), time_stamp=linestring.startpoint.timestamp)
            already_existing[0] = 1
        except Models_Point.DoesNotExist:
            geos_point_geom = geosPoint(x=linestring.startpoint.getX(), y=linestring.startpoint.getY())
            models_point_start = Models_Point(x=linestring.startpoint.getX(),
                                              y=linestring.startpoint.getY(),
                                              time_stamp=linestring.startpoint.timestamp,
                                              point_geom=geos_point_geom)
            models_point_start.save()

        try:
            models_point_end = Models_Point.objects.get(x=linestring.endpoint.getX(), y=linestring.endpoint.getY(), time_stamp=linestring.endpoint.timestamp)
            already_existing[1] = 1
        except Models_Point.DoesNotExist:
            geos_point_geom = geosPoint(x=linestring.endpoint.getX(), y=linestring.endpoint.getY())
            models_point_end = Models_Point(x=linestring.endpoint.getX(), y=linestring.endpoint.getY(),
                                            time_stamp=linestring.endpoint.timestamp, point_geom=geos_point_geom)
            models_point_end.save()




        #geos_lineString_geom = GEOSGeometry(str(linestring.ogrLinestring), srid=25832)
        #geos_buffer = geos_lineString_geom.buffer(parameters['distance'])
        #linestring = Models_Line_String(start_point=models_point_start, end_point=models_point_end, start_time=models_point_start.time_stamp, end_time=models_point_end.time_stamp, personal_id = str(linestring.personal_id), line_geom=geos_lineString_geom, buffer_geom=geos_buffer)
        #linestring.save()
        if already_existing == [0,0]:
            geos_lineString_geom = GEOSGeometry(str(linestring.ogrLinestring), srid=25832)
            geos_buffer = geos_lineString_geom.buffer(parameters['distance'])
            linestring = Models_Line_String(start_point=models_point_start,
                                                end_point=models_point_end,
                                                start_time=models_point_start.time_stamp,
                                                end_time=models_point_end.time_stamp,
                                                personal_id=str(linestring.personal_id),
                                                line_geom=geos_lineString_geom,
                                                buffer_geom=geos_buffer)
            try:
                linestring.save()
            except:
                existingID = Models_Line_String.objects.get(start_point=models_point_start, end_point=models_point_end).personal_id
        else:
            existingID = Models_Line_String.objects.get(start_point=models_point_start,
                                                    end_point=models_point_end).personal_id

    return existingID

def get_infected_outof_db():
    '''
    Database request of all linestrings
    :return: list of linestring (following the schema of the business logic)
    '''
    time_delta_14days = datetime.timedelta(days=14)
    datetime_now = datetime.datetime.now()
    datetime_now = datetime.datetime(2019, 7, 14)
    time_before_14days = datetime_now - time_delta_14days
    ergebnis_query_set = Models_Line_String.objects.filter(start_time__gt=time_before_14days) #__gt beudetet greater than


    infected_lines = list()
    print("Ich erstelle jetzt die Listen aus den DB Objekten")
    for element in ergebnis_query_set:
        ogrPoint = ogr.CreateGeometryFromWkt(element.start_point.point_geom.wkt)
        start_point = Point(ogrPoint, timestamp=element.start_time)
        ogrPoint = ogr.CreateGeometryFromWkt(element.end_point.point_geom.wkt)
        end_point = Point(ogrPoint, timestamp=element.end_time)
        buffer_geom = ogr.CreateGeometryFromWkt(element.buffer_geom.wkt)
        linestring_geom = ogr.CreateGeometryFromWkt(element.line_geom.wkt)

        linestring = Linestring(startpoint=start_point, endpoint=end_point, personal_id=element.personal_id, ogrLinestring=linestring_geom, ogrBuffer=buffer_geom)
        infected_lines.append(linestring)
    print("Jetzt bin ich fertig mit den Listen")
    return infected_lines
