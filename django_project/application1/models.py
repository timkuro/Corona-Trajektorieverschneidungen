from django.db import models

from django.db import models
import datetime
from django.contrib.gis.db import models as gismodels
from django.contrib.gis.geos import LineString, Point as geosPoint

# Create your models here.


class Point(models.Model):
    x = models.FloatField(null=True, blank=True, default=None)
    y = models.FloatField(null=True, blank=True, default=None)
    time_stamp = models.DateTimeField(default=datetime.datetime.now)

    def __str__(self):
        return f'X: {self.x}, Y: {self.y}, TimeStamp: {self.time_stamp}'

class Line_String(models.Model):
    personel_id = models.CharField(max_length=255, blank=True)
    start_time = models.DateTimeField(null=True, blank=True, default=None)
    end_time = models.DateTimeField(null=True, blank=True, default=None)
    linienSegment = gismodels.LineStringField(null=True, blank=True, default=None, srid=25832)

    def __str__(self):
        return "Anfangspunkt: {}, Endpunkt: '{}'".format(self.start_time, self.end_time)

class KML_File(models.Model):
    name = models.CharField(max_length=255, blank=True)
    file = models.FileField()
