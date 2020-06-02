from django.conf.urls import url
from django.urls import path

from . import views
app_name = 'application1'
urlpatterns = [
    url(r'^$', views.einzel_Punkt_Anzeige, name='einzel_Punkt_Anzeige'),
    #url(r'^(?P<point_id>\d+)/$', views.point_detail, name='point_detail'),
    path('<int:question_id>/', views.detail, name='detail'),
]