from functools import wraps
import requests
import urllib

OVERPASS = "https://overpass-api.de/api/interpreter/"

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
                    time.sleep(5)
            return ret
        return wrapper
    return retry

@retry_request_multi(5)
def overpass_call(query):
    encoded = urllib.parse.quote(query.encode("utf-8"), safe='~()*!.\'')
    r = requests.post(OVERPASS,
                      data=f"data={encoded}",
                      headers={"Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"})
    if not r.status_code is 200:
        raise requests.exceptions.HTTPError('Overpass server respond with status '+str(r.status_code))
    return r.text
