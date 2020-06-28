from django.conf.urls import url
from django.urls import path

from . import views
app_name = 'application1'
urlpatterns = [
    path('upload/infected', views.post_infected_file, name='post_infected_file'),
    path(r'upload/healthy', views.post_healthy_file, name='post_healthy_file'),
    path(r'download/lines/infected', views.get_all_infected_lines_outof_db, name='get_all_infected_lines_outof_db'),
    path('download/lines/infected/<str:personal_id>/', views.get_infected_lines_outof_db, name='get_infected_lines_outof_db'),
    path('delete/infected/<str:personal_id>/', views.delete_infected_lines, name='delete_infected_lines'),
    path(r'download/points/infected', views.get_all_infected_points_outof_db, name='get_all_infected_points_outof_db'),
    path(r'show/id/lines', views.get_ids_of_infected_person, name='get_ids_of_infected_person'),

]