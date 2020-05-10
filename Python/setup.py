import ez_setup
from setuptools import setup
ez_setup.use_setuptools()

setup(
    name = "corona_location_history_intersection",
    version = "1.0",
    author = "Blindert, Kurowski, Koert",
    description = ("Analyzing the location history of one or more persons to determine possible contact zones withe one corona infected person"),
    keywords = "location history corona risk contact",
    py_modules=['Geometries', 'Utilities'],
    install_requieres = ['GDAL']
)