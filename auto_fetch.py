import sys
import requests
import pandas as pd
from io import StringIO
from requests.models import Response
from pandas import json_normalize
from typing import NoReturn, Tuple, Optional, Union
import codecs

CSV_DELIMITER = ","

CONTENT_TYPE_JSON = "application/json"
CONTENT_TYPE_CSV = "text/csv"

JSON_FORMAT = "JSON"
CSV_FORMAT = "CSV"


SCHEMA_FIELD_KEY = "field"
SCHEMA_TYPE_KEY = "type"
SCHEMA_PRIMARY_KEY = "primary_key"
SCHEMA_EXAMPLE_DATA_KEY = "example_data"
SCHEMA_DESCRIPTION_KEY = "descrition"

DATA_FORMAT_KEY = "format"
DATA_TEXT_DATA_KEY = "text_data"
DATA_SCHEMA_KEY = "schema"
RESPONSE_STATUS_KEY = "response_status"

def tis2utf(tis:str)-> str :
    """
    แปลงภาษาไทย จาก TIS620 to UTF
    """
    s = ""
    for c in tis :
        if 0xa0 <= ord(c) <= 0xfb :
            s+= chr(ord(c) + 0xe00 - 0xa0)
        else :
            s+= c 
    return s 
def parse_alien_language(r : Response) -> str:
    """
    แปลงภาษาไทย
    """
    txt = r.text
    txt = tis2utf(txt)
    try :
        return txt.encode('cp1252').decode('tis-620')
    except UnicodeEncodeError :
        try:
            return bytes(r.content).decode(r.apparent_encoding)
        except :
            try:
                return codecs.decode(r.content,r.apparent_encoding)
            except :
                return txt 
    

def get_columns_json(df : pd.DataFrame) -> list :
    """
    คืนค่า ลิตของ field ของข้อมูลที่ได้รับมาจาก json
    """
    columns=list()
    column_names = df.columns.values.tolist()
    df_list   = df.values.tolist()
    for column_name_index in range(df.shape[1]) :
        first_row = df_list[0][column_name_index]
        column_name = column_names[column_name_index]
        d_type =  df[column_name].dtype
        if d_type == list :
            if (type(first_row)  == list) : 
                if (len(first_row) and  (type(first_row[0]) in [list, object,dict])) :
                    prefix = column_name+"."
                    new_df = json_normalize(first_row)
                    somethings = [ {**s, "field" : prefix+s["field"]} for s in get_columns_json(new_df)]
                    columns +=   (somethings)
                    
                    continue
        column_data = {
            SCHEMA_FIELD_KEY : column_name,
            SCHEMA_TYPE_KEY :  type(first_row).__name__,
            SCHEMA_PRIMARY_KEY : False ,
            SCHEMA_EXAMPLE_DATA_KEY :  first_row ,
            SCHEMA_DESCRIPTION_KEY : ""
        }
        columns.append(column_data)
    return columns
    
def get_json_columns(data : Union[dict,list] ) -> Optional[list]:
    """
        คืนค่า ลิตของ field ของข้อมูลที่ได้รับมาจาก json 
        ในกรณีที่แปลง เป็น  json เป็น dataframe ได้จะคืนค่า  None 
    """
    try :
        df = json_normalize(data)

        return get_columns_json(df)
    except :
        return None

def parse_to_json(r : Response) -> Tuple[Optional[list],str]:
    """
        คืนค่า
            -  ลิตของ fields
            -  ข้อมูลหลังจัดการกับภาษาไทยแล้ว
    """
    text_data = parse_alien_language(r)
    data =  r.json()
    schema = get_json_columns(data)
    
    return (schema,text_data) 

def get_columns_csv(df : pd.DataFrame) -> list :
    """
        คืนค่า ลิตของฟิลด์(คอลัมน์)
    """
    columns = list()
    column_names = df.columns.values.tolist()
    df_list   = df.values.tolist()
    for column_name_index in range(df.shape[1]) :
        first_row = df_list[0][column_name_index]
        column_data = {
            SCHEMA_FIELD_KEY : column_names[column_name_index],
            SCHEMA_TYPE_KEY :  type(first_row).__name__,
            SCHEMA_PRIMARY_KEY : False ,
            SCHEMA_EXAMPLE_DATA_KEY : first_row,
            SCHEMA_DESCRIPTION_KEY : ""
        }
        columns.append(column_data)
    return columns
    
def get_csv_columns(text : str) -> Optional[list] :
    """
        คืนค่า ลิตของฟิลด์(คอลัมน์) โดยที่หากข้อมูลที่ได้รับมาไม่สามารถแปลงเป็น dataframe ได้ จะคืนค่า None
    """
    try :
        text_data = StringIO(text)
        df = pd.read_csv(text_data)
        return get_columns_csv(df)
    except : 
        return None

def parse_to_csv(r:Response) -> Tuple[Optional[list],str]:
    """
        คืนค่า
            -  ลิตของ fields
            -  ข้อมูลหลังจัดการกับภาษาไทยแล้ว
    """
  
    text_data  = parse_alien_language(r)
    schema = get_csv_columns(text_data)
    return (schema,text_data)

def get_format(content_type : str) -> Optional[str] :
    """
        คืนค่า format ของข้อมูลในที่ได้รับ 
            ข้อมูลเป็น CSV หรือ JSON เท่านั้น อื่นๆ คืนค่า None
    """

    if CONTENT_TYPE_JSON in content_type :
        return JSON_FORMAT
    elif CONTENT_TYPE_CSV in content_type :
        return CSV_FORMAT
    else :
        return None

def get_data_by_format(data_format : str,r:Response) ->Tuple[Optional[list],Optional[str]] :
    """
        คืนค่า ข้อมูลที่ได้รับจากการ การโหลด จาก url
            -  ลิตของ fields ที่ได้จากข้อมูล
            -  ข้อมูลหลังจัดการกับภาษาไทยแล้ว
            ในกรณีที่ข้อมูล format ของข้อมูลไม่ได้อยู่ในรูปของ JSON หรือ CSV จะ คืนค่า None,None
    """
    switcher = {
        JSON_FORMAT : parse_to_json,
        CSV_FORMAT : parse_to_csv
    }
    return  switcher.get(data_format,lambda : (None,None))(r)


def parse_data(r : Response,data : dict) -> dict:
    """
        คืนค่า ข้อมูลที่ได้รับการจัดวางในรูปแบบของ dict โดยมี เนื้อหาเป็น format ของข้อมูล, ลิตต์ของฟิลด์, ข้อมูลในรูปแบบของชุดอักษร
    """
    data[DATA_FORMAT_KEY]  = get_format(r.headers['content-type'])
    data[DATA_SCHEMA_KEY], data[DATA_TEXT_DATA_KEY] = get_data_by_format(data[DATA_FORMAT_KEY],r)
    return data
    

def get_request(api :str ) -> dict:
    """
        คืนค่า ข้อมูลที่ได้รับจาก url โดยจัดให้อยู่ในรูปแบบของ dict ซึ่งประกอบด้วย HTTP status code,format ของข้อมูล, ลิตต์ของฟิลด์, ข้อมูลในรูปแบบของชุดอักษร
    """
    r = requests.get(api)
    response_status  = r.status_code
    data = {
        RESPONSE_STATUS_KEY  : response_status,
        DATA_FORMAT_KEY  :None,
        DATA_SCHEMA_KEY : None,
        DATA_TEXT_DATA_KEY : None
    }
    if r.ok : 
        data = parse_data(r,data)
        
        
    return data


##  PATH FILTER ##

def field_path_filter(data :  list,path : str) ->  list :
    """
    data  ลิตของฟิลด์ทั้งหมดที่อยู่ในข้แมูล
    path  path ของฟิลด์ทั่งต้องการให้คืนค่า ในกรณีที่ต้องการให้คืนค่าฟิลด์ ที่อยู่ซ้อนกันให้คั่นด้วยจุด(.)
    คืนค่า  ลิตของฟิลด์ที่ปรากฏใน path 
    """
    if path.strip():
        path_list = path.split('.')
        schema = data
        new_schema = []
        for column in schema :
            field = column['field']
            field_list = field.split('.')
            check  = all(path in field_list for path in path_list)
            check_order = field.startswith(path)
            if check  and check_order:
                new_schema.append(column)
        return new_schema
    else :
        return  data 


def data_path_filter(data : dict,path:str) :
    """
    data ข้อมูลทั้งหมด
    path path ของฟิลด์ทั่งต้องการให้คืนค่า ในกรณีที่ต้องการให้คืนค่าฟิลด์ ที่อยู่ซ้อนกันให้คั่นด้วยจุด(.)
    คืนค่า dict ของข้อมูลที่อยู่ในผ่านการกรอง
    """
    data_pool  = [data]
    json_data = None
    if path.strip():
        path_list = path.split('.')
        for key_index in range(len(path_list)) :
            key = path_list[key_index]
            if type(data_pool[key_index]) is dict :
                if  key in data_pool[key_index] : 

                    cat_data = data_pool[key_index][key]
                    data_pool.append(cat_data) 
                    json_data = cat_data
            elif  type (data_pool[key_index]) is list :
                
                list_data = []
                for item in data_pool[key_index] :
                    if key in item :
                        list_data.append(
                            item[key]
                        )
                data_pool.append(list_data)
                json_data = list_data
            else :
                else_data = data_pool[key_index]
                data_pool.append(else_data)
                json_data = else_data
                      
        return json_data
    else :
        return data 


### EASY FUNC ####

import json
from io import  StringIO
import urllib.parse
from typing import  Tuple


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




if __name__ == '__main__' :
    url = sys.argv[1]
    path_filter = None
    data = get_data(url=url,path_filter=path_filter)
