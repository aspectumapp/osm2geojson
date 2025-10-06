set -e
./lint.sh
python -m unittest discover
rm -rf dist
python -m build
