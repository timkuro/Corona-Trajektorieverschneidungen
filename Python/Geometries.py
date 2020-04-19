import arcpy

class Point:
    def __init__(self, x, y, timestamp):
        self.x = x
        self.y = y
        self.timestamp = timestamp

    def __str__(self):
        return (self.x + " " + self.y + " " + self.timestamp)

class Linestring:
    def __init__(self, startpoint, endpoint):
        self.startpoint = startpoint
        self.endpoint = endpoint

    def intersect(self, other_line):
        self_arcpy = arcpy.Polyline(arcpy.Array([arcpy.Point(self.startpoint.x, self.startpoint.y), arcpy.Point(self.endpoint.x, self.endpoint.y)]))
        other_arcpy = arcpy.Polyline(arcpy.Array([arcpy.Point(other_line.startpoint.x, other_line.startpoint.y), arcpy.Point(other_line.endpoint.x, other_line.endpoint.y)]))
        intersect_point = self_arcpy.intersect(other_arcpy, 1)

        if intersect_point:
            cross_point = Crosspoint(Point(intersect_point.firstPoint.X, intersect_point.firstPoint.Y, None), self, other_line)
            return cross_point
        else:
            raise Exception("No intersection found")

    def __str__(self):
        return str(self.startpoint) + " " + str(self.endpoint)

class Crosspoint:
    def __init__(self, point, line1, line2):
        self.point = point
        self.line1 = line1
        self.line2 = line2


'''test = (Linestring(Point(1,1, None), Point(1,2, None)).intersect(Linestring(Point(2,1, None), Point(2, 2, None))))
test = (Linestring(Point(1,1, "2020-02-29"), Point(1,2,  "2020-02-30")).intersect(Linestring(Point(2,1, "2020-02-28"), Point(1, 2, "2020-02-29"))))
print(type(test))
print(test)
if not test:
    print('keine geometrie')
#print(str(test.firstPoint.X) + " " + str(test.firstPoint.Y))