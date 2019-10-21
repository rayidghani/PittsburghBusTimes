
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

logging.basicConfig(level=logging.ERROR)
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


def search(stop_ids,routes):
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
        'stpid': stop_ids,
        'rt': routes,
        'format':'json'
    }
    return request(API_HOST, PREDICTIONS_PATH, url_params=url_params)


def nextbustime(origin):
    stop_id, direction, buses = setparams(origin)
    dict_buses = get_bus_info(stop_id,buses)
    logger.info('dict buses is %s', dict_buses)
    for i in range(0,len(dict_buses['bustime-response']['prd'])):
        bus = dict_buses['bustime-response']['prd'][i]
        if bus['prdctdn'] == 'DUE':
            bus['prdctdn'] = '0'
        if bus['rtdir'] == direction:
            return int(bus['prdctdn'])

def allbustimes(origin):
    stop_id, direction, buses = setparams(origin)
    dict_buses = get_bus_info(stop_id,buses)
    logger.debug('dict buses is %s', dict_buses)
    bustimes=[]
    for i in range(0,len(dict_buses['bustime-response']['prd'])):
        bus = dict_buses['bustime-response']['prd'][i]
        if bus['prdctdn'] == 'DUE':
            bus['prdctdn'] = '0'
        if bus['rtdir'] == direction:
            bustimes.append(int(bus['prdctdn']))
    return bustimes

def leavenow(origin, gap_threshold):
    bustimes = allbustimes(origin)
    if len(bustimes) > 1:
        bustimes.sort()
        differences = [t - s for s, t in zip(bustimes, bustimes[1:])]
        differences.sort()
        if any(x > gap_threshold for x in differences):
            # all bus times before the gap and the gap
            return 1
        else:
            return 0
    else:
        logger.info('only 1 bus time') 
        return ''

def setparams(origin):
    if (origin == 'home'):
        stop_id = 10920
        direction = 'INBOUND'
    elif (origin == 'work'):
        stop_id = 7117
        direction = 'OUTBOUND'
    else:
        logger.error('undefined origin')
    buses='61C,61D'

    return stop_id, direction, buses

def get_bus_info(stop_id,buses):
    search_api_response = search(stop_id,buses)
    return json.loads(search_api_response)


def main():

    origin = 'work'
    a = nextbustime(origin)
    print('next bus is in',a)

    b = allbustimes(origin)
    print('next buses are in',b)

    c = leavenow(origin, 10)
    if c:
        print('leave', allbustimes(origin))
    else:
        print('stay')

  
if __name__== "__main__":
  main()
     
# input: origin: home or office
# outputs
# 1. next bus time
# 2. all bus times returned
# 3. leave in x minutes because a gap is coming
