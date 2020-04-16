class Point:
    def __init__(self, id, x, y, timestamp):
        self.id = id
        self.x = x
        self.y = y
        self.timestamp = timestamp

class Linestring:
    def __init__(self, startpoint, endpoint):
        self.id = id
        self.startpoint = startpoint
        self.endpoint = endpoint

    def intersect(self, other_line):
        pass

class Crosspoint:
    def __init__(self, point, lambda1, lambda2, line1, line2):
        self.point = point
        self.lambda1 = lambda1
        self.lambda2 = lambda2
        self.line1 = line1
        self.line2 = line2