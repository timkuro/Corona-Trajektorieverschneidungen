from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, Http404
from django.shortcuts import render
# Create your views here.
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from Business_Logic.Utilities import *
from application1.models import Point

from Business_Logic.Geometries import Point, Linestring
from django.contrib.gis.geos import LineString as Geos_LineString, GEOSGeometry
from application1.models import Point as Models_Point, Line_String as Models_Line_String
class Home(TemplateView):
    template_name = 'home.html'

def einzel_Punkt_Anzeige(request):
    '''
    template = loader.get_template('trajectory/points.html')
    context = RequestContext(request, {'point': Point.objects.all()})
    return HttpResponse(template.render(context))
    '''

    zeilen = []
    for m in Point.objects.all():
        zeilen.append("Point: vom {}".format(m.time_stamp.isoformat()))
        zeilen.append('X-Koordinate: {}'.format(m.x))
        zeilen.append('Y-Koordinate: {}'.format(m.y))
        zeilen += ['', '-'*30, '']
    antwort = HttpResponse('\n'.join(zeilen))
    antwort['Content-Type'] = 'text/plain'
    return  antwort

def detail(request, question_id):
    return HttpResponse("You're looking at question %s." % question_id)



def point_detail(request, point_id):
    try:
        p = Point.objects.get(id=point_id)
    except Point.DoesNotExist:
        raise Http404
    zeilen = [
        "Dies ist eine weitere Methode/View um Objekte abzufragen",
        "Point: vom {}".format(p.time_stamp.isoformat()),
        'X-Koordinate: {}'.format(p.x),
        'Y-Koordinate: {}'.format(p.y),
        '', '-' * 30, '',
        "Blablabla"]
    antwort = HttpResponse('\n'.join(zeilen))
    antwort['Content-Type'] = 'text/plain'
    return antwort


def multiple_buttons(request):
    if request.method == 'POST' and 'uploadBtn' in request.POST:
        print("Upload")
        print(request)
        corona_contacts = simple_upload(request.FILES)
        return render(request, 'application1/simple_upload.html', {
            'uploaded_file_url': corona_contacts
        })
    if request.method == 'POST' and 'startBtn' in request.POST:
        print("Start")
    return render(request, 'application1/simple_upload.html')

'''
def simple_upload(files):
    urls = list()
    fs = FileSystemStorage()
    for file in files.getlist('infected_file'):
        new_file_name = file.name.split(".")[-2] + "_infected" + ".kml"
        if not fs.exists(new_file_name):
            fs.save(new_file_name, file)
            uploaded_file_url = fs.url(new_file_name)
            list_linestrings = read_kml_line("./"+uploaded_file_url)
            splitted_lines_list = split_line(list_linestrings, '2019-07-01T00:00:00Z', '2019-08-01T00:00:00Z', new_file_name.split(".")[-2])
            #write_in_database(splitted_lines_list)
    for file in files.getlist('healthy_file'):
        new_file_name = file.name.split(".")[-2] + "_healthy" + ".kml"
        if not fs.exists(new_file_name):
            fs.save(new_file_name, file)
        uploaded_file_url = fs.url(new_file_name)
        urls.append(uploaded_file_url)
    return urls
'''



def simple_upload(files):
    infected_persons = []
    test_persons = []
    infectedLines = []
    healthyLines = []

    fs = FileSystemStorage()
    for file in files.getlist('infected_file'):
        new_file_name = file.name.split(".")[-2] + "_infected" + ".kml"
        if not fs.exists(new_file_name):
            fs.save(new_file_name, file)
        uploaded_file_url = fs.url(new_file_name)
        list_linestrings = read_kml_line("./" + uploaded_file_url)
        splitted_lines_list = split_line(list_linestrings, '2019-07-01T00:00:00Z', '2019-08-01T00:00:00Z', new_file_name.split(".")[-2])
        infected_persons.append(splitted_lines_list)

    for file in files.getlist('healthy_file'):
        new_file_name = file.name.split(".")[-2] + "_healthy" + ".kml"
        if not fs.exists(new_file_name):
            fs.save(new_file_name, file)
        uploaded_file_url = fs.url(new_file_name)
        list_linestrings = read_kml_line("./" + uploaded_file_url)
        splitted_lines_list = split_line(list_linestrings, '2019-07-01T00:00:00Z', '2019-08-01T00:00:00Z', new_file_name.split(".")[-2])
        test_persons.append(splitted_lines_list)
        healthyLines = splitted_lines_list


    for element in infected_persons:
        infectedLines += element

    infectedLines, healthyLines = boundingBox_intersection(infectedLines, healthyLines)

    result_geom = intersect_geom(infectedLines, healthyLines, distance=10)
    result_time = intersect_time(result_geom, delta=datetime.timedelta(minutes=15))
    convert_crossline_to_shapefile(result_time,fs.base_location, "corona_contacts")

    return fs.url("corona_contacts.shp")


'''
def simple_upload(request):
    print(request.FILES)
    print(request.FILES.getlist('infected_file'))
    urls = list()
    if request.method == 'POST' and request.FILES:
        fs = FileSystemStorage()
        for file in request.FILES.getlist('infected_file'):
            new_file_name = file.name.split(".")[-2] + "_infected" + ".kml"
            if not fs.exists(new_file_name):
                fs.save(new_file_name, file)
            uploaded_file_url = fs.url(new_file_name)
            urls.append(uploaded_file_url)

        for file in request.FILES.getlist('healthy_file'):
            new_file_name = file.name.split(".")[-2] + "_healthy" + ".kml"
            if not fs.exists(new_file_name):
                fs.save(new_file_name, file)
            uploaded_file_url = fs.url(new_file_name)
            urls.append(uploaded_file_url)
        return render(request, 'application1/simple_upload.html', {
            'uploaded_file_url': urls
        })
    return render(request, 'application1/simple_upload.html')
'''

def workflow(urls_list_healthy):
    for kml_file in urls_list_healthy:
        kml_infected = read_kml_line(kml_file)
        lines1 = split_line(kml_infected, '2019-07-01T00:00:00Z', '2019-08-01T00:00:00Z', kml_file.split(".")[-2])
    #write_in_database(lines1)

@csrf_exempt
def post_infected_file(request):
    if request.method == 'POST':
        kml = request.body
        list_linestrings = read_kml_line(kml)
        splitted_lines = split_line(list_linestrings, '2019-07-01T00:00:00Z', '2019-08-01T00:00:00Z', personal_id="Christian", sourceEPSG=4326)
        #write_in_database(splitted_lines, "Christian")
        return HttpResponse("Finished Uploading")
    return  HttpResponse("Please use a POST-Request")


@csrf_exempt
def post_healthy_file(request):
    if request.method == 'POST':
        kml = request.body
        list_linestrings = read_kml_line(kml)
        healthyLines = split_line(list_linestrings, '2019-07-01T00:00:00Z', '2019-08-01T00:00:00Z', personal_id="Christian", sourceEPSG=4326)

        infectedLines = []
        infectedLines, healthyLines = boundingBox_intersection(infectedLines, healthyLines)




        return HttpResponse("Finished Uploading")
    return  HttpResponse("Please use a POST-Request")


def write_in_database(list_linestring, personal_id):
    for linestring in list_linestring:
        #geos_lineString_geom = Geos_LineString((linestring.startpoint.getX(), linestring.startpoint.getY()), (linestring.endpoint.getX(), linestring.endpoint.getY()), srid=4326)
        #print(linestring.ogrLinestring)
        geos_lineString_geom = GEOSGeometry(str(linestring.ogrLinestring), srid=25832)
        models_point_start = Models_Point(x=linestring.startpoint.getX(), y=linestring.startpoint.getY(), time_stamp=linestring.startpoint.getTimestamp())
        models_point_end = Models_Point(x=linestring.endpoint.getX(), y=linestring.endpoint.getY(), time_stamp=linestring.endpoint.getTimestamp())
        models_point_start.save()
        models_point_end.save()
        linestring = Models_Line_String(start_time=models_point_start.time_stamp, end_time=models_point_end.time_stamp, linienSegment=geos_lineString_geom)
        linestring.save()

def get_infected_outof_db(personal_id):
    ergebnis_query_set = Models_Line_String.objects.filter(personal_id=personal_id)
    infected_lines = []
    for element in ergebnis_query_set:
        #linestring = Linestring(element.linienSegment, element.end_time,)
        pass