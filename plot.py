import plotly
from plotly.graph_objs import Scatter, Layout
import json
import csv
import argparse
import os
from datetime import datetime

def excel_time_to_datetime(time):
    return datetime.strptime(time, '%x %X')

def get_trace(trace_name, data_dir):
    filename = data_dir + '/' + trace_name + '.csv'
    duration = []
    time = []
    with open(filename, 'rb') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)
        for row in reader:
            duration.append(float(row[2])/60)
            time.append(excel_time_to_datetime(row[1].strip()))

    return Scatter(
        x = time,
        y = duration,
        mode = 'lines',
        name = trace_name
    )

parser = argparse.ArgumentParser(description='Upload commute time data to Plotly')
parser.add_argument('input', type=argparse.FileType('r'), help='JSON file listing the start and end destinations. See input.json.sample for example.')
args = parser.parse_args()
inputs = json.loads(args.input.read())['inputs']

data_dir = os.path.dirname(os.path.realpath(__file__)) + '/data'

for path in inputs:
    trace_out = get_trace(path['name']+'_out', data_dir)
    trace_back = get_trace(path['name']+'_back', data_dir)
    plotly.plotly.plot(
        {
            'data': [trace_out, trace_back],
            'layout': {
                'title': 'Daily Commute'
            }
        },
        filename=path['name'] + ' commute',
        sharing='public'
    )
