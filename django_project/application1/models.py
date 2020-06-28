from django.db import models

from django.db import models
import datetime
from django.contrib.gis.db import models as gismodels

# Create your models here.


class Point(models.Model):
    x = models.FloatField(null=True, blank=True, default=None)
    y = models.FloatField(null=True, blank=True, default=None)
    time_stamp = models.DateTimeField(default=datetime.datetime.now)
    point_geom = gismodels.PointField(null=True, blank=True, default=None, srid=25832)

    class Meta:
        unique_together = ('x', 'y', 'time_stamp')

    def __str__(self):
        return f'X: {self.x}, Y: {self.y}, TimeStamp: {self.time_stamp}'


class Line_String(models.Model):
    personal_id = models.CharField(max_length=255, blank=True)
    start_point = models.ForeignKey(Point, on_delete=models.CASCADE, related_name='start_point', default=None)
    end_point = models.ForeignKey(Point, on_delete=models.CASCADE, related_name='end_point', default=None)
    start_time = models.DateTimeField(null=True, blank=True, default=None)
    end_time = models.DateTimeField(null=True, blank=True, default=None)
    line_geom = gismodels.LineStringField(null=True, blank=True, default=None, srid=25832)
    buffer_geom = gismodels.PolygonField(null=True, blank=True, default=None, srid=25832)

    class Meta:
        unique_together = ('start_point', 'end_point')

    def __str__(self):
        return "Anfangspunkt: {}, Endpunkt: '{}'".format(self.start_time, self.end_time)
