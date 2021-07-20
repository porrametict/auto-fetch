import sys
import requests
from typing import Optional

from .config import *
from .json import parse_to_json
from .csv import parse_to_csv


def get_format(content_type : str) -> Optional[str] :
    """
        คืนค่า format ของ content_type ที่ได้รับ
        โดย content_type จะต้อง ระบุข้อมูลใน body เป็น CSV หรือ JSON เท่านั้น อื่นๆ คืนค่า None

    Args:
        content_type (str): headers['conten-type'] ของ response

    Returns:
        Optional[str]: รูปแบบของข้อมูลที่ได้จาก content-type 
    """

    if CONTENT_TYPE_JSON in content_type :
        return JSON_FORMAT
    elif CONTENT_TYPE_CSV in content_type :
        return CSV_FORMAT
    else :
        return None

def get_data_by_format(data_format : str,r) -> tuple :    
    """
    คืนค่าข้อมูล ที่ได้จากการแปลง response โดยจะคืนค่าเป็น tuple ที่มีข้อมูลดังนี้
        -  ลิสขอฟิลด์ที่ได้จากข้อมูล
        -  ข้อมูล(string)หลังจัดการกับภาษาไทยแล้ว
    *ในกรณีที่ไม่สามารถแปลงข้อมูลได้คืนค่าเป็น (None,None,None)

    Args:
        data_format (str): รูปแบบของข้อมูล (JSON หรือ CSV เท่านั้น)
        r (response): response ที่ได้จากการเรียก request

    Returns:
        tuple: tupleของฟิล์ข้อมูลและstringข้อมูล ตามลำดับ
    """
    switcher = {
        JSON_FORMAT : parse_to_json,
        CSV_FORMAT : parse_to_csv
    }
    return  switcher.get(data_format,lambda : (None,None,None))(r)


def parse_data(r) -> dict:
    """
        แปลง response ให้อยู้ในรูปแบบที่ต้องการ คืนค่าในรูปแบบ dict โดยมีรายละเอียดดังนี้
            - รูปแบบของข้อมูล
            - สคีมาของข้อมูล
            - ข้อมูลในรูปแบบสติง
            - ข้อมูลในรูปแบบที่เหมาะสม

    Args:
        r (response): response ที่ได้จากการเรียก request

    Returns:
        dict: dict ของข้อมูลที่ได้ response 
    """

    data = dict()
    data[DATA_FORMAT_KEY]  = get_format(r.headers['content-type'])
    data[DATA_SCHEMA_KEY], data[DATA_TEXT_DATA_KEY],data[DATA_PARSED_DATA_KEY] = get_data_by_format(data[DATA_FORMAT_KEY],r)
    return data
    

def get_request(url :str ) -> dict:
    """
        ข้อมูลที่ได้รับจากการเรียก url ที่ได้รับ  
        โดยจัดให้อยู่ในรูปแบบของ dict ซึ่งประกอบด้วย 
            - url
            - format ของข้อมูล 
            - สคีมา
            - ข้อมูลในรูปแบบของชุดอักษร
            - ข้อมูลในรูปแบบที่เหมาะสม


    Args:
        url (str): ลิงก์ของที่อยู่ของข้อมูล (ข้อมูลต้องเป็น JSON และ CSV เท่านั้น)

    Returns:
        dict:  ข้อมูลที่ได้รับจากการเรียก url ที่ถูกจัดให้อยู่ในรูปแบบข้างต้น
    """
    data = {
        DATA_URL_KEY : url,
        DATA_FORMAT_KEY  :None,
        DATA_SCHEMA_KEY : None,
        DATA_TEXT_DATA_KEY : None,
        DATA_PARSED_DATA_KEY : None,
    }
   
    r = requests.get(url)
    
    if r.ok : 
        parsed_data = parse_data(r)
        data.update(parsed_data)
    return data


if __name__ == "__main__" :
    data = get_request(sys.argv[1])
