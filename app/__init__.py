from flask import Flask, render_template, request
from .fetch_data.request_data import get_request
from.fetch_data.path_filter import data_path_filter, field_path_filter
import json
app = Flask(__name__)


@app.route('/', methods=['GET'])
def index():
    data = {
        'url': None,
        "path_filter": None
    }
    return render_template('index.html', data=data)


@app.route('/', methods=['POST'])
def index_post():
    data = {
        'url': None,
        "path_filter": None
    }

    url = request.form.get('url')
    path_filter = request.form.get('path_filter')


    method = request.form.get('method')
    if method == 'get_request' : 
        data = get_request(url)
    elif method == 'path_filter':
        data = get_request(url)
        full_json_data = data['parsed_data']
        full_schema = data['schema']
        schema = field_path_filter(full_schema,path_filter)
        json_data = data_path_filter(full_json_data,path_filter)
        data['schema'] = schema
        data['text_data'] = json.dumps(json_data)
        data['path_filter'] =  path_filter
    
    return render_template('index.html', data=data)
