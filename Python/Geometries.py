import arcpy
from time import localtime
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference(25832)
arcpy.env.geographicTransformations = "ETRS_1989_To_WGS84"

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
        Berechnet zu jeder Linie einen Puffer und verschneidet diese
    '''
    def intersect_Buffer(self, other_line):
        self_arcpy =  arcpy.Polyline(arcpy.Array([arcpy.Point(self.startpoint.x, self.startpoint.y), arcpy.Point(self.endpoint.x, self.endpoint.y)]), arcpy.SpatialReference(4326))
        other_arcpy = arcpy.Polyline(arcpy.Array([arcpy.Point(other_line.startpoint.x, other_line.startpoint.y), arcpy.Point(other_line.endpoint.x, other_line.endpoint.y)]), arcpy.SpatialReference(4326))

        self_buffer = self_arcpy.buffer(0.002)
        other_buffer = other_arcpy.buffer(0.002)
        intersect_buffer = self_buffer.intersect(other_buffer, 4)

        if intersect_buffer:
            cross_area = Crossarea(intersect_buffer, self, other_line)
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

class Crossarea:
    def __init__(self, polygon, line1, line2):
        self.polygon = polygon
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