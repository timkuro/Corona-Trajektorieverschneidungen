from time import localtime
from osgeo import ogr, osr

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

    __ogr_Buffer = None

    def __init__(self, ogrLinestring, startpoint, endpoint, personal_id=None):
        self.personal_id = personal_id
        self.startpoint = startpoint
        self.endpoint = endpoint

        self.ogrLinestring = ogrLinestring

    def __init__(self, startpoint, endpoint, personal_id=None):
        self.personal_id = personal_id
        self.startpoint = startpoint
        self.endpoint = endpoint

        self.ogrLinestring = ogr.Geometry(ogr.wkbLineString)
        self.ogrLinestring.AddPoint_2D(startpoint.getX(), startpoint.getY())
        self.ogrLinestring.AddPoint_2D(endpoint.getX(), endpoint.getY())

    def intersect_Buffer(self, other_line, distance):
        '''
        DEPRECATED
        Intersects the buffers two lines

        :param other_line: line to be intersected
        :param distance: buffer size
        :return: crossing area
        '''

        self_ogr = self.ogrLinestring
        other_ogr = other_line.ogrLinestring

        self_buffer = self_ogr.Buffer(distance)

        other_buffer = other_ogr.Buffer(distance)
        intersect_buffer = self_buffer.Intersection(other_buffer)

        if intersect_buffer:
            cross_area = Cross_Geometry(intersect_buffer, self, other_line)
            return cross_area
        else:
            raise Exception("No intersection found")

    def intersect_Buffer_line(self, other_line, distance):
        '''
        Intersects a line with a buffer of an other line

        :param other_line:
        :param distance:
        :return:
        '''
        self_ogr = self.ogrLinestring
        other_ogr = other_line.ogrLinestring

        if self.__ogr_Buffer == None:
            self.__ogr_Buffer = self_ogr.Buffer(distance)
        self_buffer = self.__ogr_Buffer

        intersect_buffer_line = self_buffer.Intersection(other_ogr)

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