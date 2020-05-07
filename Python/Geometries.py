from time import localtime
from osgeo import ogr
class Point:
    def __init__(self, x, y, timestamp):
        self.x = x
        self.y = y
        self.timestamp = timestamp

    def __repr__(self):
        return f"Point:[X:{self.x}, Y: {self.y}, TimeStamp: {self.timestamp}]"


class Linestring:
    def __init__(self, startpoint, endpoint):
        self.startpoint = startpoint
        self.endpoint = endpoint

    '''
        Verschneidet Linien
    '''
    '''
    def intersect_Lines(self, other_line):
        self_arcpy = arcpy.Polyline(arcpy.Array([arcpy.Point(self.startpoint.x, self.startpoint.y), arcpy.Point(self.endpoint.x, self.endpoint.y)]))
        other_arcpy = arcpy.Polyline(arcpy.Array([arcpy.Point(other_line.startpoint.x, other_line.startpoint.y), arcpy.Point(other_line.endpoint.x, other_line.endpoint.y)]))
        intersect_point = self_arcpy.intersect(other_arcpy, 1)

        if intersect_point:
            cross_point = Crosspoint(Point(intersect_point.firstPoint.X, intersect_point.firstPoint.Y, None), self, other_line)
            return cross_point
        else:
            raise Exception("No intersection found")
    '''

    '''
        Berechnet zu jeder Linie einen Puffer und verschneidet diese
    '''
    def intersect_Buffer(self, other_line, distance):
        self_ogr = ogr.Geometry(ogr.wkbLineString)
        self_ogr.AddPoint(self.startpoint.x, self.startpoint.y)
        self_ogr.AddPoint(self.endpoint.x, self.endpoint.y)

        other_ogr = ogr.Geometry(ogr.wkbLineString)
        other_ogr.AddPoint(other_line.startpoint.x, other_line.startpoint.y)
        other_ogr.AddPoint(other_line.endpoint.x, other_line.endpoint.y)

        #self_arcpy =  arcpy.Polyline(arcpy.Array([arcpy.Point(self.startpoint.x, self.startpoint.y), arcpy.Point(self.endpoint.x, self.endpoint.y)]), arcpy.SpatialReference(4326))
        #other_arcpy = arcpy.Polyline(arcpy.Array([arcpy.Point(other_line.startpoint.x, other_line.startpoint.y), arcpy.Point(other_line.endpoint.x, other_line.endpoint.y)]), arcpy.SpatialReference(4326))

        bufferDistance = (distance*360)/40000000
        self_buffer = self_ogr.Buffer(bufferDistance)
        #print(self_buffer.ExportToWkt())
        other_buffer = other_ogr.Buffer(bufferDistance)
        intersect_buffer = self_buffer.Intersection(other_buffer)
        #print (intersect_buffer.ExportToWkt())

        if intersect_buffer:
            cross_area = Cross_Geometry(intersect_buffer, self, other_line)
            return cross_area
        else:
            raise Exception("No intersection found")

    '''
            Berechnet zu jeder Linie einen Puffer und verschneidet diese
    '''
    def intersect_Buffer_line(self, other_line, distance):
        self_ogr = ogr.Geometry(ogr.wkbLineString)
        self_ogr.AddPoint(self.startpoint.x, self.startpoint.y)
        self_ogr.AddPoint(self.endpoint.x, self.endpoint.y)

        bufferDistance = (distance * 360) / 40000000
        self_buffer = self_ogr.Buffer(bufferDistance)

        other_ogr = ogr.Geometry(ogr.wkbLineString)
        other_ogr.AddPoint(other_line.startpoint.x, other_line.startpoint.y)
        other_ogr.AddPoint(other_line.endpoint.x, other_line.endpoint.y)

        intersect_buffer_line = self_buffer.Intersection(other_ogr)

        if intersect_buffer_line:
            cross_area = Cross_Geometry(intersect_buffer_line, self, other_line)
            return cross_area
        else:
            raise Exception("No intersection found")

    def __repr__(self):
        return f"Line:[ {self.startpoint} ,  {self.endpoint} ]"

class Crosspoint:
    def __init__(self, point, line1, line2):
        self.point = point
        self.line1 = line1
        self.line2 = line2

    def __repr__(self):
        return f"Crosspoint[{self.point}, 1: {self.line1}, 2: {self.line2}]"

class Cross_Geometry:
    def __init__(self, geometry, line1, line2):
        self.geometry = geometry
        self.line1 = line1
        self.line2 = line2

    def __repr__(self):
        return f"Crossarea[{self.polygon}, 1: {self.line1}, 2: {self.line2}]"

if __name__ == "__main__":
    test = (Linestring(Point(1,1, "2020-02-29"), Point(1,2,  "2020-02-30")).intersect_Lines(Linestring(Point(2,1, "2020-02-28"), Point(1, 2, "2020-02-29"))))
    print(type(test))
    print(test)
    if not test:
        print('keine geometrie')
    #print(str(test.firstPoint.X) + " " + str(test.firstPoint.Y))