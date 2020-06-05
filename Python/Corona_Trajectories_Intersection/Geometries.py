from time import localtime
from osgeo import ogr, osr
from config import parameters

class Point:
    '''
    Point Object

    __ogrPoint: Type ogrGeometry
    __timestamp: Type datetime
    '''

    def __init__(self, ogrPoint, timestamp):
        self.__ogrPoint = ogrPoint
        self.__timestamp = timestamp

    def getX(self):
        return self.__ogrPoint.GetX()
    def getY(self):
        return self.__ogrPoint.GetY()
    def getGeometry(self):
        return self.__ogrPoint
    def getTimestamp(self):
        return self.__timestamp

    def __repr__(self):
        return f"Point:[X:{self.getX()}, Y: {self.getY()}, TimeStamp: {self.timestamp}]"

    geometry = property(getGeometry)
    timestamp = property(getTimestamp)

class Linestring:
    '''
        Linestring Object

        personal_id: Type String
        startpoint: Type Point
        endpoint: Type Point
        ogrLinestring: Type ogrGeometry
    '''

    def __init__(self, startpoint, endpoint, personal_id, ogrLinestring=None, ogrBuffer=None):
        self.startpoint = startpoint
        self.endpoint = endpoint

        self.personal_id = personal_id

        if ogrLinestring is None:
            self.ogrLinestring = ogr.Geometry(ogr.wkbLineString)
            self.ogrLinestring.AddPoint_2D(startpoint.getX(), startpoint.getY())
            self.ogrLinestring.AddPoint_2D(endpoint.getX(), endpoint.getY())
        else:
            self.ogrLinestring = ogrLinestring

        if ogrBuffer is None:
            self.ogr_Buffer = self.ogrLinestring.Buffer(parameters['distance'])
        else:
            self.ogr_Buffer = ogrBuffer

    def intersect_Buffer(self, other_line):
        '''
        DEPRECATED
        Intersects the buffers two lines

        :param other_line: line to be intersected
        :return: crossing area
        '''

        intersect_buffer = self.ogr_Buffer.Intersection(other_line.ogrBuffer)

        if intersect_buffer:
            cross_area = Cross_Geometry(intersect_buffer, self, other_line)
            return cross_area
        else:
            raise Exception("No intersection found")

    def intersect_Buffer_line(self, other_line):
        '''
        Intersects a line with a buffer of an other line

        :param other_line:
        :return:
        '''

        intersect_buffer_line = self.ogr_Buffer.Intersection(other_line.ogrLinestring)

        if intersect_buffer_line:
            cross_area = Cross_Geometry(intersect_buffer_line, self, other_line)
            return cross_area
        else:
            raise Exception("No intersection found")

    def __repr__(self):
        return f"Line:[ {self.ogrLinestring} ]"

class Cross_Geometry:
    def __init__(self, geometry, line1, line2):
        self.geometry = geometry
        self.line1 = line1
        self.line2 = line2

    def __repr__(self):
        return f"Crossgeometry[{self.geometry}, 1: {self.line1}, 2: {self.line2}]"

if __name__ == "__main__":
    pass