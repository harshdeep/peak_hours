import requests
import datetime
import json
import os.path
import pytz
from pytz import timezone
from datetime import datetime
import argparse
import time

API_BASE_URL = "https://maps.googleapis.com/maps/api/directions/json"

def api_call(path, query_params, api_key):
    query_params['key'] = api_key
    return requests.get(API_BASE_URL + path, params=query_params)

def duration(origin, destination, api_key):
    r = api_call('', {
            'destination': destination,
            'origin': origin,
            'traffic_model': 'best_guess',
            'mode': 'driving',
            'departure_time': 'now'
        },
        api_key)
    if (r.status_code != 200):
        raise Exception('API Call Failed. ' + r.text)
    r = r.json()
    if (r['status'] != 'OK'):
        raise Exception('API Call Failed. ' + r['error_message'])
    return r['routes'][0]['legs'][0]['duration_in_traffic']['value']

def current_time_in_pst():
    date = datetime.now(tz=pytz.utc)
    return date.astimezone(timezone('US/Pacific'))

def datetime_to_timestamp(date):
    return int(time.mktime(date.timetuple()))

def excel_time(time):
    return time.strftime('%x %X')

def append_duration(filepath, origin, destination, api_key):
    d = duration(origin, destination, api_key)
    f = None
    if not os.path.isfile(filepath):
        f = open(filepath, 'w+')
        f.write('Timestamp, Time, Duration\n')
    else:
        f = open(filepath, 'a')

    time = current_time_in_pst()
    f.write('{0}, {1}, {2}\n'.format(datetime_to_timestamp(time), excel_time(time), d))
    f.close()

parser = argparse.ArgumentParser(description='Take commute time snapshot')
parser.add_argument('input', type=argparse.FileType('r'), help='JSON file listing the start and end destinations. See input.json.sample for example.')
parser.add_argument('config', type=argparse.FileType('r'), help='JSON file containing your app configuration, particularly Google Maps API key. See config.json.sample for example.')
args = parser.parse_args()
inputs = json.loads(args.input.read())['inputs']
api_key = json.loads(args.config.read())['google_api_key']

data_dir = os.path.dirname(os.path.realpath(__file__)) + '/data'
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

for path in inputs:
    out_csv = data_dir + '/' + path['name'] + '_out.csv'
    append_duration(out_csv, path['origin'], path['destination'], api_key)
    back_csv = data_dir + '/' + path['name'] + '_back.csv'
    append_duration(back_csv, path['destination'], path['origin'], api_key)
