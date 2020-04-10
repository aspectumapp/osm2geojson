from os import path

from setuptools import setup

dirname = path.abspath(path.dirname(__file__))
with open(path.join(dirname, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='osm2geojson',
    version='0.1.20',
    license='MIT',
    description='Parse OSM and Overpass JSON',
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords='geometry gis osm parsing',
    author='Parfeniuk Mykola',
    author_email='mikola.parfenyuck@gmail.com',
    packages=['osm2geojson'],
    include_package_data=True,
    install_requires=['shapely', 'requests']
)
