from os import path
from setuptools import setup
try:
    # for pip >= 10
    from pip._internal.req import parse_requirements
except ImportError:
    # for pip <= 9.0.3
    from pip.req import parse_requirements

dirname = path.abspath(path.dirname(__file__))
with open(path.join(dirname, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

def load_requirements(fname):
    reqs = parse_requirements(fname, session="test")
    return [str(ir.req) for ir in reqs]

setup(
    name='osm2geojson',
    version='0.1.22',
    license='MIT',
    description='Parse OSM and Overpass JSON',
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords='geometry gis osm parsing',
    author='Parfeniuk Mykola',
    author_email='mikola.parfenyuck@gmail.com',
    packages=['osm2geojson'],
    include_package_data=True,
    install_requires=load_requirements("requirements.txt")
)
