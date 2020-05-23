# coding=utf-8
import os, sys
import datetime
from Utilities import *



if __name__ == "__main__":
    path_timmy=r"C:\Users\Tim\hs-bochum.de\Christian Koert - GI_Projekt_Wytzisk\Standortverlauf_Juli_2019"
    path_tommy=r"D:\hs-bochum.de\Christian Koert - GI_Projekt_Wytzisk\Standortverlauf_Juli_2019"
    path_kort=r"C:\Users\chris\OneDrive - hs-bochum.de\GI_Projekt_Wytzisk\Standortverlauf_Juli_2019"

    if(os.environ['USERNAME'] == "Thomas"):
        path = path_tommy
    elif(os.environ['USERNAME'] == "Tim"):
        path = path_timmy
    elif(os.environ['USERNAME'] == "chris"):
        path = path_kort

    export_path = path.split("\\")

    print(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ') + "  Lese erste Datei als kranke Person")

    datei1 = read_kml_line(path[:-len(export_path[-1])] + "Standortverlauf_Juli_2019\Standortverlauf_Christian_Juli2019.kml")

    print(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ') + "  Anzahl Punkte: " + str(len(datei1) / 2 - 1) + " Punkte")
    print(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ') + "  Splitte erste Datei")

    lines1 = split_line(datei1, '2019-07-01T00:00:00Z', '2019-08-01T00:00:00Z', "krank_Christian")

    print(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ') + "  Anzahl Linien: " + str(len(lines1)) + " Linien")
    print(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ') + "  Exportiere erste gesplittete Datei")

    #convert_linestring_to_shapefile(lines1, path[:-len(export_path[-1])] + r"Ergebnisse\Splitted_Lines", "Splitted_Lines_Tim_Juli2019_ogr")

    print(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ') + "  Erste Linie gesplittet")


    print(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ') + "  Lese zweite Datei als gesunde Person")

    datei2 = read_kml_line(path[:-len(export_path[-1])] + "Standortverlauf_Juli_2019\Standortverlauf_Tim_Juli2019.kml")

    print(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ') + "  Anzahl Punkte: " + str(len(datei2)/2 - 1) + " Punkte")
    print(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ') + "  Splitte zweite Datei")

    lines2 = split_line(datei2, '2019-07-01T00:00:00Z', '2019-08-01T00:00:00Z', "gesund_Tim")

    print(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ') + "  Anzahl Linien: " + str(len(lines2)) + " Linien")
    print(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ') + "  Exportiere zweite gesplittete Datei")

    #convert_linestring_to_shapefile(lines2, path[:-len(export_path[-1])] + r"Ergebnisse\Splitted_Lines", "Splitted_Lines_Christian_Juli2019_ogr")

    print(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ') + "  Zweite Linie gesplittet")


    print(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ') + "  Lese dritte Datei als gesunde Person")

    datei3 = read_kml_line(path[:-len(export_path[-1])] + "Standortverlauf_Juli_2019\Standortverlauf_Thomas_Juli2019.kml")

    print(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ') + "  Anzahl Punkte: " + str(
        len(datei2) / 2 - 1) + " Punkte")
    print(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ') + "  Splitte dritte Datei")

    lines3 = split_line(datei2, '2019-07-01T00:00:00Z', '2019-08-01T00:00:00Z', "gesund_Thomas")

    print(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ') + "  Anzahl Linien: " + str(len(lines2)) + " Linien")
    print(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ') + "  Exportiere dritte gesplittete Datei")

    # convert_linestring_to_shapefile(lines2, path[:-len(export_path[-1])] + r"Ergebnisse\Splitted_Lines", "Splitted_Lines_Christian_Juli2019_ogr")

    print(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ') + "  Dritte Linie gesplittet")


    infectedLines = lines1
    healthyLines = lines2 + lines3


    bboxInfected = create_bounding_box(infectedLines)
    bboxHealthy = create_bounding_box(healthyLines)

    infectedLines = intersect_bounding_box(infectedLines, bboxHealthy)
    healthyLines = intersect_bounding_box(healthyLines, bboxInfected)


    convert_linestring_to_shapefile(infectedLines, path[:-len(export_path[-1])] + r"Ergebnisse\Splitted_Lines",
                                    "Splitted_Lines_Christian_Juli2019_ogr")
    convert_linestring_to_shapefile(healthyLines, path[:-len(export_path[-1])] + r"Ergebnisse\Splitted_Lines",
                                    "Splitted_Lines_Tim_Juli2019_ogr")


    result_geom = intersect_geom(infectedLines, healthyLines, distance=10)
    print(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ') + "  Geometrische Intersection")
    result_time = intersect_time(result_geom, delta=datetime.timedelta(minutes=15))
    print(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ') + "  Zeitliche Intersection")

    convert_crossline_to_shapefile(result_time, path[:-len(export_path[-1])] + r"Ergebnisse\Schnitt_Zeitlich", "time_intersection_tim_christian_abgabe")
    print(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ') + "  Ergebnis geschrieben")