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
        myline = arcpy.Polyline(arcpy.Array([arcpy.Point(self.startpoint.x, self.startpoint.y), arcpy.Point(self.endpoint.x, self.endpoint.y)]))
        otherline = arcpy.Polyline(arcpy.Array([arcpy.Point(other_line.startpoint.x, other_line.startpoint.y), arcpy.Point(other_line.endpoint.x, other_line.endpoint.y)]))
        if myline.intersect(otherline, 1):
            return True
        else:
            return False

    def __str__(self):
        return str(self.startpoint) + " " + str(self.endpoint)

class Crosspoint:
    def __init__(self, point, lambda1, lambda2, line1, line2):
        self.point = point
        self.lambda1 = lambda1
        self.lambda2 = lambda2
        self.line1 = line1
        self.line2 = line2


'''test = (Linestring(Point(1,1, None), Point(1,2, None)).intersect(Linestring(Point(2,1, None), Point(2, 2, None))))
print(type(test))
if not test:
    print('keine geometrie')
#print(str(test.firstPoint.X) + " " + str(test.firstPoint.Y))'''