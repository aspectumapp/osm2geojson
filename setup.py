from setuptools import setup

setup(
   name='osm2geojson',
   version='0.1',
   description='Parse OSM and JOSM',
   author='rapkin (Parfeniuk Mykola)',
   author_email='mikola.parfenyuck@gmail.com',
   packages=['osm2geojson'],
   install_requires=['shapely']
)
