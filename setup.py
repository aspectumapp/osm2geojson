from setuptools import setup
from os import path

dirname = path.abspath(path.dirname(__file__))
with open(path.join(dirname, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='osm2geojson',
    version='0.1.5',
    license='MIT',
    description='Parse OSM and Overpass JSON',
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords = 'geometry gis osm parsing',
    author='Parfeniuk Mykola',
    author_email='mikola.parfenyuck@gmail.com',
    packages=['osm2geojson'],
    package_data={ '': 'osm2geojson/*.json' },
    install_requires=['shapely']
)
