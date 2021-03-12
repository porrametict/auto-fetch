from codecs import encode
from flask import Flask,render_template,request,redirect
from flask.helpers import url_for
# from .test import get_request, parse_alien_language
from .path_filter  import field_path_filter,data_path_filter
# from .test2 import get_request
import json
from io import  StringIO
import pandas as pd 
import csv
import urllib.parse
from .easy_func import get_data

app = Flask(__name__)

@app.route('/')
def index():
    url = request.args.get('url',None)
    path_filter = request.args.get('path_filter',None)

    data = get_data(url=url,path_filter=path_filter)
    return render_template('index.html',data=data,url=url,path_filter=path_filter)

@app.route('/',methods=['POST'])
def index_post () :
    url = request.form.get('url')
    return redirect(url_for('index',url=url))

@app.route("/filter",methods=['POST'])
def index_filter():
    url = request.form.get('url')
    path_filter = request.form.get('path_filter')
    

    return redirect(url_for('index',url=url,path_filter=path_filter))