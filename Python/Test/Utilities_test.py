import unittest
from Corona_Trajectories_Intersection.Utilities import *
from Corona_Trajectories_Intersection.Geometries import *
import os
from osgeo import ogr
import config


class Utilities_test(unittest.TestCase):
    '''
    Class for testing the used code snippets
    '''

    # preparation
    config.parameters['sourceEPSG'] = 25832
    cwd = os.path.abspath(os.getcwd())  # for building the path

    # read the test kml file and put it into a string (for test_read_kml_line)
    with open(cwd + r'\resources\location_history_test.kml', 'r') as file:
        location_history_test_string = file.read()
    # empty xml object for later usage


    # test objects
    # splitted lines 1
    p1_ogr = ogr.Geometry(ogr.wkbPoint)
    p2_ogr = ogr.Geometry(ogr.wkbPoint)
    p3_ogr = ogr.Geometry(ogr.wkbPoint)
    p4_ogr = ogr.Geometry(ogr.wkbPoint)
    p1_ogr.AddPoint_2D(0, 0)
    p2_ogr.AddPoint_2D(100, 100)
    p3_ogr.AddPoint_2D(200, 0)
    p4_ogr.AddPoint_2D(300, 100)

    splitted_line_1 = Linestring(Point(p1_ogr, datetime.datetime.strptime('2019-07-02T00:00:00Z', '%Y-%m-%dT%H:%M:%SZ') ), Point(p2_ogr, datetime.datetime.strptime('2019-07-03T00:00:00Z', '%Y-%m-%dT%H:%M:%SZ')), 0)
    splitted_line_2 = Linestring(Point(p2_ogr, datetime.datetime.strptime('2019-07-03T00:00:00Z', '%Y-%m-%dT%H:%M:%SZ')), Point(p3_ogr, datetime.datetime.strptime('2019-07-04T00:00:00Z', '%Y-%m-%dT%H:%M:%SZ')), 0)
    splitted_line_3 = Linestring(Point(p3_ogr, datetime.datetime.strptime('2019-07-04T00:00:00Z', '%Y-%m-%dT%H:%M:%SZ')), Point(p4_ogr, datetime.datetime.strptime('2019-07-05T00:00:00Z', '%Y-%m-%dT%H:%M:%SZ')), 0)
    expected_splitted_lines_1 = [splitted_line_1, splitted_line_2, splitted_line_3]

    # splitted lines 2
    p5_ogr = ogr.Geometry(ogr.wkbPoint)
    p6_ogr = ogr.Geometry(ogr.wkbPoint)
    p7_ogr = ogr.Geometry(ogr.wkbPoint)
    p8_ogr = ogr.Geometry(ogr.wkbPoint)
    p5_ogr.AddPoint_2D(0, 200)
    p6_ogr.AddPoint_2D(100, 0)
    p7_ogr.AddPoint_2D(200, 100)
    p8_ogr.AddPoint_2D(100, 300)

    splitted_line_4 = Linestring(Point(p5_ogr, datetime.datetime.strptime('2019-07-02T00:00:00Z', '%Y-%m-%dT%H:%M:%SZ')), Point(p6_ogr, datetime.datetime.strptime('2019-07-03T00:00:00Z', '%Y-%m-%dT%H:%M:%SZ')), 0)
    splitted_line_5 = Linestring(Point(p6_ogr, datetime.datetime.strptime('2019-07-05T00:00:00Z', '%Y-%m-%dT%H:%M:%SZ')), Point(p7_ogr, datetime.datetime.strptime('2019-07-06T00:00:00Z', '%Y-%m-%dT%H:%M:%SZ')), 0)
    splitted_line_6 = Linestring(Point(p7_ogr, datetime.datetime.strptime('2019-07-06T00:00:00Z', '%Y-%m-%dT%H:%M:%SZ')), Point(p8_ogr, datetime.datetime.strptime('2019-07-07T00:00:00Z', '%Y-%m-%dT%H:%M:%SZ')), 0)
    expected_splitted_lines_2 = [splitted_line_4, splitted_line_5, splitted_line_6]

    def test_read_kml_line(self):
        '''
        tests if the method returns the same result for text and path passing
        '''
        xml_from_file = read_kml_line(self.cwd + r'\resources\location_history_test.kml')
        xml_from_string = read_kml_line(self.location_history_test_string)
        self.assertIsNotNone(xml_from_file)
        self.assertEqual(xml_from_file.text, xml_from_string.text)

    def test_split_lines(self):
        xml_from_string = read_kml_line(self.location_history_test_string)
        splitted_lines = split_line(xml_from_string, 0)
        self.assertEqual(str(self.expected_splitted_lines_1[0]), str(splitted_lines[0]))
        self.assertEqual(str(self.expected_splitted_lines_1[1]), str(splitted_lines[1]))
        self.assertEqual(str(self.expected_splitted_lines_1[2]), str(splitted_lines[2]))

    def test_boundingBox_intersection(self):
        bbox_intersected_1 = boundingBox_intersection(self.expected_splitted_lines_1, self.expected_splitted_lines_2)
        # create expected element
        bbox_1 = ogr.Geometry(ogr.wkbPoint)
        bbox_2 = ogr.Geometry(ogr.wkbPoint)
        bbox_3 = ogr.Geometry(ogr.wkbPoint)
        bbox_1.AddPoint_2D(0, 0)
        bbox_2.AddPoint_2D(100, 100)
        bbox_3.AddPoint_2D(200, 0)
        splitted_bbox_1 = Linestring(Point(bbox_1, datetime.datetime.strptime('2019-07-02T00:00:00Z', '%Y-%m-%dT%H:%M:%SZ')), Point(bbox_2, datetime.datetime.strptime('2019-07-03T00:00:00Z', '%Y-%m-%dT%H:%M:%SZ')), 0)
        splitted_bbox_2 = Linestring(Point(bbox_2, datetime.datetime.strptime('2019-07-03T00:00:00Z', '%Y-%m-%dT%H:%M:%SZ')), Point(bbox_3, datetime.datetime.strptime('2019-07-04T00:00:00Z', '%Y-%m-%dT%H:%M:%SZ')), 0)
        expected_splitted_lines_bbox = [splitted_bbox_1, splitted_bbox_2]
        self.assertEqual(str(expected_splitted_lines_bbox[0]), str(bbox_intersected_1[0][0]))
        self.assertEqual(str(expected_splitted_lines_bbox[1]), str(bbox_intersected_1[0][1]))

    def test_intersect_geom(self):
        intersection = intersect_geom(self.expected_splitted_lines_1, self.expected_splitted_lines_2)
        # create expected element
        inter_geom_1 = ogr.Geometry(ogr.wkbPoint)
        inter_geom_2 = ogr.Geometry(ogr.wkbPoint)
        inter_geom_3 = ogr.Geometry(ogr.wkbPoint)
        inter_geom_1.AddPoint_2D(0, 0)
        inter_geom_2.AddPoint_2D(100, 100)
        inter_geom_3.AddPoint_2D(200, 0)
        splitted_inter_geom_1 = Linestring(Point(inter_geom_1, datetime.datetime.strptime('2019-07-02T00:00:00Z', '%Y-%m-%dT%H:%M:%SZ')), Point(inter_geom_2, datetime.datetime.strptime('2019-07-03T00:00:00Z', '%Y-%m-%dT%H:%M:%SZ')), 0)
        splitted_inter_geom_2 = Linestring(Point(inter_geom_2, datetime.datetime.strptime('2019-07-03T00:00:00Z', '%Y-%m-%dT%H:%M:%SZ')), Point(inter_geom_3, datetime.datetime.strptime('2019-07-04T00:00:00Z', '%Y-%m-%dT%H:%M:%SZ')), 0)

        self.assertEqual(str(splitted_inter_geom_1), str(intersection[0].line1))
        self.assertEqual(str(splitted_inter_geom_2), str(intersection[1].line1))

    def test_intersect_time(self):
        intersection = intersect_geom(self.expected_splitted_lines_1, self.expected_splitted_lines_2)
        temporal_intersection = intersect_time(intersection)

        inter_temp_1 = ogr.Geometry(ogr.wkbPoint)
        inter_temp_2 = ogr.Geometry(ogr.wkbPoint)
        inter_temp_1.AddPoint_2D(0, 0)
        inter_temp_2.AddPoint_2D(100, 100)
        splitted_inter_temp_1 = Linestring(
            Point(inter_temp_1, datetime.datetime.strptime('2019-07-02T00:00:00Z', '%Y-%m-%dT%H:%M:%SZ')),
            Point(inter_temp_2, datetime.datetime.strptime('2019-07-03T00:00:00Z', '%Y-%m-%dT%H:%M:%SZ')), 0)

        self.assertEqual(str(splitted_inter_temp_1), str(temporal_intersection[0].line1))


if __name__ == "__main__":
    unittest.main()
