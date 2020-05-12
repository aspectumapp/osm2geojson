set -e
./lint.sh
python -m unittest discover
rm -rf dist
python setup.py sdist
twine upload dist/*
