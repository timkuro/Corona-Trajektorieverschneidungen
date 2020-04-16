import xml.etree.ElementTree as ET

# reads the kml file and prepares data for further operations
def read_kml_line(path):
    tree = ET.parse(path)
    root = tree.getroot()
    if "Track" in root[0][0][1].tag:
        return root[0][0][1]
    else:
        raise Exception('no track-tag found in KML')

def split_line(input_line):
    pass

def convert_to_kml(linestrings):
    pass

def intersect_geom(linestrings):
    pass

def intersect_time(crosspoints):
    pass

print(read_kml_line(r"D:\Uni-Lokal\GI-Projekt Corona\hs-bochum.de\Christian Koert - GI_Projekt_Wytzisk\Standortverlauf_Tim_Juli2019.kml"))