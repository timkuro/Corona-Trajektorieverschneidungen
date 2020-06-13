from time import localtime
from osgeo import ogr
from config import parameters


class Point:
    '''
    Point Object

    __ogrPoint: Type ogrGeometry
    __timestamp: Type datetime
    '''

    def __init__(self, ogrPoint, timestamp):
        self.__ogrPoint = ogrPoint
        self.timestamp = timestamp

    def getX(self):
        return self.__ogrPoint.GetX()

    def getY(self):
        return self.__ogrPoint.GetY()

    def getGeometry(self):
        return self.__ogrPoint

    def __repr__(self):
        return f"Point:[X:{self.getX()}, Y: {self.getY()}, TimeStamp: {self.timestamp}]"

    geometry = property(getGeometry)


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

        self.ogr_Buffer = ogrBuffer


    def intersect_Buffer_line(self, other_line):
        '''
        Intersects a line with a buffer of an other line

        :param other_line:
        :return:
        '''

        if self.ogr_Buffer is None:
            self.ogr_Buffer = self.ogrLinestring.Buffer(parameters['distance'])

        intersect_buffer_line = self.ogr_Buffer.Intersection(other_line.ogrLinestring)

        if not ogr.Geometry.IsEmpty(intersect_buffer_line):
            cross_area = Cross_Geometry(intersect_buffer_line, self, other_line)
            return cross_area
        else:
            raise Exception("No intersection found")

    def __repr__(self):
        return f"Line:[geometry: {self.ogrLinestring}, id: {self.personal_id}, Startpoint: {self.startpoint}, Endpoint: {self.endpoint}]"


class Cross_Geometry:
    '''
            Cross_Geometry Object

            geometry: Type ogrGeometry
            line1: Type ogrGeometry
            line2: Type ogrGeometry
    '''

    def __init__(self, geometry, line1, line2):
        self.geometry = geometry
        self.line1 = line1
        self.line2 = line2

    def __repr__(self):
        return f"Crossgeometry[{self.geometry}, 1: {self.line1}, 2: {self.line2}]"


if __name__ == "__main__":
    pass
