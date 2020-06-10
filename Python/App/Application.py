# coding=utf-8
from Corona_Trajectories_Intersection.Utilities import *
import sys

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

datei1 = read_kml_line(open(path[:-len(export_path[-1])] + "Standortverlauf_Juli_2019\Standortverlauf_Christian_Juli2019.kml").read())

print(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ') + "  Anzahl Punkte: " + str((len(datei1) - 1)/2) + " Punkte")
print(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ') + "  Splitte erste Datei")

lines1 = split_line(datei1)

print(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ') + "  Anzahl Linien: " + str(len(lines1)) + " Linien")
print(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ') + "  Exportiere erste gesplittete Datei")

convert_linestring_to_shapefile(lines1, path[:-len(export_path[-1])] + r"Ergebnisse\Splitted_Lines", "Splitted_Lines_Christian_Juli2019_ogr")

print(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ') + "  Erste Linie gesplittet")


print(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ') + "  Lese zweite Datei als gesunde Person")

datei2 = read_kml_line(path[:-len(export_path[-1])] + "Standortverlauf_Juli_2019\Standortverlauf_Tim_Juli2019.kml")

print(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ') + "  Anzahl Punkte: " + str((len(datei2) - 1)/2) + " Punkte")
print(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ') + "  Splitte zweite Datei")

lines2 = split_line(datei2, "gesund_Tim")

print(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ') + "  Anzahl Linien: " + str(len(lines2)) + " Linien")
print(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ') + "  Exportiere zweite gesplittete Datei")

convert_linestring_to_shapefile(lines2, path[:-len(export_path[-1])] + r"Ergebnisse\Splitted_Lines", "Splitted_Lines_Tim_Juli2019_ogr")

print(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ') + "  Zweite Linie gesplittet")


print(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ') + "  Lese dritte Datei als gesunde Person")

datei3 = read_kml_line(path[:-len(export_path[-1])] + "Standortverlauf_Juli_2019\Standortverlauf_Thomas_Juli2019.kml")

print(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ') + "  Anzahl Punkte: " + str((len(datei3) - 1)/2) + " Punkte")
print(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ') + "  Splitte dritte Datei")

lines3 = split_line(datei3)

print(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ') + "  Anzahl Linien: " + str(len(lines3)) + " Linien")
print(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ') + "  Exportiere dritte gesplittete Datei")

convert_linestring_to_shapefile(lines3, path[:-len(export_path[-1])] + r"Ergebnisse\Splitted_Lines", "Splitted_Lines_Thomas_Juli2019_ogr")

print(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ') + "  Dritte Linie gesplittet")


infectedLines = lines1
healthyLines = lines2 + lines3

if len(infectedLines) == 0 or len(healthyLines) == 0:
    raise Exception("Keine Eingabedaten")

infectedLines, healthyLines = boundingBox_intersection(infectedLines, healthyLines)


convert_linestring_to_shapefile(infectedLines, path[:-len(export_path[-1])] + r"Ergebnisse\Splitted_Lines",
                                "Splitted_Lines_Krank_Juli2019_ogr")
convert_linestring_to_shapefile(healthyLines, path[:-len(export_path[-1])] + r"Ergebnisse\Splitted_Lines",
                                "Splitted_Lines_Gesund_Juli2019_ogr")
print(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ') + "  Linestrings auf Projektgebiet reduziert")


result_geom = intersect_geom(infectedLines, healthyLines)
print(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ') + "  Geometrische Intersection")
result_time = intersect_time(result_geom)
print(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ') + "  Zeitliche Intersection")

convert_crossline_to_shapefile(result_time, path[:-len(export_path[-1])] + r"Ergebnisse\Schnitt_Zeitlich", "time_intersection_tim_christian_abgabe")
print(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ') + "  Ergebnis geschrieben")