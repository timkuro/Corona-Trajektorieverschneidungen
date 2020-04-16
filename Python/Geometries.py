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
        pass

    def __str__(self):
        return str(self.startpoint) + " " + str(self.endpoint)

class Crosspoint:
    def __init__(self, point, lambda1, lambda2, line1, line2):
        self.point = point
        self.lambda1 = lambda1
        self.lambda2 = lambda2
        self.line1 = line1
        self.line2 = line2