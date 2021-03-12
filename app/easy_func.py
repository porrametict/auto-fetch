
from app.path_filter import data_path_filter, field_path_filter
import json
from io import  StringIO
import pandas as pd  
import urllib.parse
from typing import  Tuple
from .request_data import  get_request


CHANGE_JSON_SCHEMA = True
CHANGE_DATA = True


def csv_to_list(string_csv: str ) -> Tuple[list,list]:
    """
    แปลง CSV ในอยู่ในรูปของ List
    คืนค่า
        - ลิตของข้อมูลของแต่ละแถว ยกเว้นบรรทัดแรก
        - ลิตของข้อมูลของบรรทัดแรก (มองว่าบรรทัดแรกเป็นหัวตารางเสมอ)
    """
    text_data = StringIO(string_csv)
    df = pd.read_csv(text_data)
    header = list(df.columns)
    content_list = df.values.tolist()
    return content_list,header


def get_data(url : str =None,path_filter: str=None ) -> dict:
    """
    คืนค่าข้อมูลที่ถอดได้จาก url 
    * ข้อมูลเพื่มเติม -> README.md
    """
    
    if(url):
        url = urllib.parse.unquote(url)
        url = url.replace(";","&")
        data =  get_request(url)
        
        if data['format'] == "JSON" :
            data['text_data'] = data['text_data'].replace("\'","\"")
            data['pretty_data'] = data['text_data']
        elif data['format'] == "CSV" :
            data["csv_items"],data["csv_headers"] = csv_to_list(data['text_data'])
        data['schema_json'] = {"schema" : data['schema']}
        data['pure_schema'] = data['schema']


        if path_filter and data['pure_schema'] :
            data['schema'] = field_path_filter(data=data['pure_schema'],path=path_filter)
            if CHANGE_JSON_SCHEMA :
                data['schema_json'] = {"schema" : data['schema']}
            if CHANGE_DATA and data['format'] == "JSON" :
                json_data = json.loads(data['text_data'])   
                data['pretty_data'] = json.dumps(data_path_filter(json_data,path_filter))

        return  data
    else :
        return {}
