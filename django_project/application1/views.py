import zipfile
from zipfile import ZipFile

from django.core.files.storage import FileSystemStorage
from django.core.serializers import serialize
from django.http import HttpResponse
from django.shortcuts import render
# Create your views here.
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from Business_Logic.database_connection import *
from application1.models import Point as Models_Point, Line_String as Models_Line_String

infected_persons = []
test_persons = []

class Base(TemplateView):
    template_name = 'base.html'

def request_formular(request):
    '''

    :param request:
    :return:
    '''
    if request.method == 'POST' and 'uploadBtn' in request.POST:
        print("Upload")
        print(request)
        file_url, healthy_id = simple_upload(request.FILES)
        return render(request, 'application1/formular.html', {
            'uploaded_file_url': file_url,
            'uploaded_file_id': healthy_id,
        })
    return render(request, 'application1/formular.html')


def simple_upload(files):
    '''
    Reading the formular data, escpecially the input files (multiple)
    :param files: The request.FILES dictionary
    :return: a zipped shapefile of all intersectionsSHP with a infected person
    '''
    infectedLines = []
    healthyLines = []

    fs = FileSystemStorage()
    for file in files.getlist('infected_file'):
        #new_file_name = file.name.split(".")[-2] + "_infected" + ".kml"
        #uploaded_file_url = fs.url(new_file_name)
        list_linestrings = read_kml_line(file.read())
        splitted_lines_list = split_line(list_linestrings)
        infected_persons.append(splitted_lines_list)

    for file in files.getlist('healthy_file'):
        #new_file_name = file.name.split(".")[-2] + "_healthy" + ".kml"
        #uploaded_file_url = fs.url(new_file_name)
        list_linestrings = read_kml_line(file.read())
        splitted_lines_list = split_line(list_linestrings)
        test_persons.append(splitted_lines_list)
        healthyLines = splitted_lines_list


    for element in infected_persons:
        infectedLines += element

    print(len(infectedLines))
    #for element in test_persons:
       # healthyLines += element
    print("BBOX zeug")
    infectedLines, healthyLines = boundingBox_intersection(infectedLines, healthyLines)
    print("Geom zeug")
    result_geom = intersect_geom(infectedLines, healthyLines)
    print(result_geom[0])
    print("Time zeug")
    result_time = intersect_time(result_geom)
    print("Shape zeug")
    output_file_name = str(healthyLines[0].personal_id)
    #if fs.exists(output_file_name):
    #    fs.delete(output_file_name)
    convert_crossline_to_shapefile(result_time,f"{fs.base_location}\intersectionsSHP", output_file_name)

    filenames = [f"{output_file_name}.shp", f"{output_file_name}.dbf", f"{output_file_name}.shx",
                 f"{output_file_name}.prj"]

    with ZipFile(fs.base_location + f'\intersectionsZIP\{output_file_name}.zip', 'w') as zip:
        # writing each file one by one
        for file in filenames:
            file = f"media\intersectionsSHP\{file}"
            zip.write(file)
            fs.delete(file)

    return (fs.url(f"{output_file_name}.zip"), output_file_name)


@csrf_exempt
def post_infected_file(request):
    '''
    Request to post a kml file from Google Takeout of a infected person
    The file (14 days, depending on the config file) is stored in a database
    :param request: HTTP POST Request
    :return: HttpResponse which confirmes a successfull upload
    '''
    if request.method == 'POST':
        kml = request.body
        list_linestrings = read_kml_line(kml)
        splitted_lines = split_line(list_linestrings)
        id = write_in_database(splitted_lines)
        return HttpResponse("Finished Uploading, your ID is " + str(id))
    return  HttpResponse("Please use a POST-Request")

@csrf_exempt
def post_healthy_file(request):
    '''
    Request to post a kml file from Google Takeout of a healthy person
    The file is not stored in a database
    :param request: HTTP POST Request
    :return: HttpResponse with a zipped shapefile
    '''
    print(datetime.datetime.now())
    fs = FileSystemStorage()
    if request.method == 'POST':
        kml = request.body
        list_linestrings = read_kml_line(kml)
        healthyLines = split_line(list_linestrings)
        infectedLines = get_infected_outof_db()
        print(healthyLines[0])
        print(infectedLines[0])
        print("/n =====================================================================================================================")
        infectedLines, healthyLines = boundingBox_intersection(infectedLines, healthyLines)
        result_geom = intersect_geom(infectedLines, healthyLines)
        print("jetzt bin ich hier")
        result_time = intersect_time(result_geom)
        print("jetzt bin ich da")
        output_file_name = str(healthyLines[0].personal_id)
        #if fs.exists(output_file_name):
         #   fs.delete(output_file_name)
        convert_crossline_to_shapefile(result_time, f"{fs.base_location}\intersectionsSHP", output_file_name)
        print("jetzt bin ich dort")

        filenames = [f"{output_file_name}.shp", f"{output_file_name}.dbf", f"{output_file_name}.shx",
                     f"{output_file_name}.prj"]

        zip_filename = f"media\intersectionsZIP\{output_file_name}.zip"
        response = HttpResponse(content_type='application/zip')
        zip_file = zipfile.ZipFile(response, 'w')
        for file in filenames:
            file = f"media\intersectionsSHP\{file}"
            zip_file.write(file)
            fs.delete(file)
        response['Content-Disposition'] = 'attachment; filename={}'.format(zip_filename)
        zip_file.close()
        return response

        #return zip_files()
    return  HttpResponse("Please use a POST-Request")






@csrf_exempt
def get_all_infected_lines_outof_db(request):
    '''
    Request to obtain all lines in the database
    :param request: HTTP GET Request
    :return: HTTPResponse with a geojson
    '''
    geojson = serialize('geojson', Models_Line_String.objects.all(),
                        geometry_field='line_geom',
                        fields=("personal_id", "start_time", "end_time"), srid=25832)
    return HttpResponse(geojson)



def get_all_infected_points_outof_db(request):
    '''
    Request to obtain all Points in the database
    :param request: HTTP GET Request
    :return: HTTPResponse with a geojson
    '''
    geojson = serialize('geojson', Models_Point.objects.all(),
              geometry_field='point_geom',
              fields=("time_stamp"), srid=25832)
    return HttpResponse(geojson)


@csrf_exempt
def get_infected_lines_outof_db(request, personal_id):
    '''
    Request to obtain all lineStrings of a particular person
    :param request: HTTP GET Request
    :param personal_id:  Personal ID, which the user data were assigned to
    :return: HTTPResponse with a geojson
    '''
    geojson = serialize('geojson', Models_Line_String.objects.filter(personal_id=personal_id),
                        geometry_field='line_geom',
                        fields=("personal_id", "start_time", "end_time"), srid=25832)
    return HttpResponse(geojson)


def delete_infected_lines(request, personal_id):
    '''
    Removes the (only) data of the lineStringObjects from the database
    :param request:  HTTP GET Request
    :param personal_id:  Personal ID, which the user data were assigned to
    :return: HttpResponse which is confirming the removing
    '''
    queryset = Models_Line_String.objects.filter(personal_id=personal_id)
    if len(queryset) != 0:
        queryset.delete()
        return HttpResponse(f"Delete {personal_id} from the database")
    else:
        return HttpResponse(f"{personal_id} is already deleted")


@csrf_exempt
def get_ids_of_infected_person(request):
        '''
        Request to obtain personal IDs of infected persons stored in the database
        :param request: HTTP GET Request
        :return: HTTPResponse simple text
        '''
        queryset = Models_Line_String.objects.exclude().values_list('personal_id', flat=True).distinct()
        zeilen = []
        for element in queryset:
            zeilen.append(element)
            zeilen += ['', '-' * 30, '']
        antwort = HttpResponse('\n'.join(zeilen))
        antwort['Content-Type'] = 'text/plain'
        return antwort
