import codecs
import os
import urllib
from functools import wraps
from time import sleep

import requests

OVERPASS = "https://overpass-api.de/api/interpreter/"
dirname = os.path.dirname(os.path.dirname(__file__))


def read_data_file(name):
    path = os.path.join(dirname, 'tests/data', name)
    with codecs.open(path, 'r', encoding='utf-8') as data:
        return data.read()


def retry_request_multi(max_retries):
    def retry(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            num_retries = 0
            while num_retries <= max_retries:
                try:
                    ret = func(*args, **kwargs)
                    break
                except requests.exceptions.HTTPError:
                    if num_retries == max_retries:
                        raise
                    num_retries += 1
                    sleep(5)
            return ret
        return wrapper
    return retry


@retry_request_multi(5)
def overpass_call(query):
    encoded = urllib.parse.quote(query.encode("utf-8"), safe='~()*!.\'')
    r = requests.post(OVERPASS,
                      data="data={}".format(encoded),
                      headers={"Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"})
    if not r.status_code == 200:
        raise requests.exceptions.HTTPError(
            'Overpass server respond with status '+str(r.status_code))
    return r.text
