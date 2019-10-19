
from __future__ import print_function
from __future__ import absolute_import

import argparse
import json
import pprint
import requests
import sys
import os
import shutil
import sys
import logging
from urllib.request import urlopen
from bs4 import BeautifulSoup
import xmltodict


# This client code can run on Python 2.x or 3.x.  Your imports can be
# simpler if you only need one of those.
try:
    # For Python 3.0 and later
    from urllib.error import HTTPError
    from urllib.parse import quote
    from urllib.parse import urlencode
except ImportError:
    # Fall back to Python 2's urllib2 and urllib
    from urllib2 import HTTPError
    from urllib import quote
    from urllib import urlencode

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


PGH_API_KEY = os.environ.get('PGH_API_KEY')
if PGH_API_KEY:
    logger.debug('Loaded Yelp API Key %s', PGH_API_KEY)
else:
    logger.error('No environment variable set for  API key - set PGH_API_KEY=XXX')

# API constants, you shouldn't have to change these.
API_HOST = 'http://realtime.portauthority.org/bustime/api/v3/'
PREDICTIONS_PATH = 'getpredictions'


def request(host, path, url_params=None):
    """Given your API_KEY, send a GET request to the API.
    Args:
        host (str): The domain host of the API.
        path (str): The path of the API after the domain.
        API_KEY (str): Your API Key.
        url_params (dict): An optional set of query parameters in the request.
    Returns:
        dict: The JSON response from the request.
    Raises:
        HTTPError: An error occurs from the HTTP request.
    """
    url_params = url_params or {}
    url = '{0}{1}'.format(host, quote(path.encode('utf8')))

    logger.info('Querying %s with url params %s ...', url, url_params)

    response = requests.request('GET', url, headers='', params=url_params, verify=False)
    logger.debug('querying returned json %s',response.json())
    return response.text


def search(stopids,routes):
    """Query the Search API by a search term and location.

    Args:
        location (str): The search location passed to the API.
        num_of_businesses_to_get (int): # of businesses you want to get 

    Returns:
        dict: The JSON response from the request.
    """
    # change here to get different categories or search terms
    # todo: load from config file
    url_params = {
        'key': PGH_API_KEY,
        'rtpidatafeed': 'Port Authority Bus',
        'stpid': stopids,
        'rt': routes,
        'format':'json'
    }
    return request(API_HOST, PREDICTIONS_PATH, url_params=url_params)


def main():
  
  origin = 'home'
  NEXT_ONLY = 0

  if (origin == 'home'):
    stopid = 10920
    direction = 'INBOUND'
  elif (origin == 'work'):
    stopid = 7117
    direction = 'OUTBOUND'

  buses='61C,61D'
  
  a = search(stopid,buses)
  dict_obj = json.loads(a)
  #print(dict_obj)
  for i in range(0,len(dict_obj['bustime-response']['prd'])):
    bus = dict_obj['bustime-response']['prd'][i]
    if bus['rtdir'] == direction:
        print(bus['prdctdn'])
        if NEXT_ONLY:
            break
  
if __name__== "__main__":
  main()

