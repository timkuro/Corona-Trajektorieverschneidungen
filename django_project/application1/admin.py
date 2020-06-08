from django.contrib import admin

# Register your models here.
from application1.models import Point, Line_String

admin.site.register(Point)
admin.site.register(Line_String)