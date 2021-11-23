from os import path
from setuptools import setup

dirname = path.abspath(path.dirname(__file__))
with open(path.join(dirname, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

def parse_requirements(filename):
    lines = (line.strip() for line in open(path.join(dirname, filename)))
    return [line for line in lines if line and not line.startswith("#")]

setup(
    name='osm2geojson',
    version='0.1.30',
    license='MIT',
    description='Parse OSM and Overpass JSON',
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords='geometry gis osm parsing',
    author='Parfeniuk Mykola',
    author_email='mikola.parfenyuck@gmail.com',
    url='https://github.com/aspectumapp/osm2geojson',
    packages=['osm2geojson'],
    include_package_data=True,
    install_requires=parse_requirements("requirements.txt")
)
