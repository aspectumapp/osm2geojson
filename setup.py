from setuptools import setup

setup(
    name='osm2geojson',
    version='0.1',
    license='MIT',
    description='Parse OSM and Overpass JSON',
    keywords = 'geometry gis osm parsing',
    author='Parfeniuk Mykola',
    author_email='mikola.parfenyuck@gmail.com',
    packages=['osm2geojson'],
    install_requires=['shapely']
)
