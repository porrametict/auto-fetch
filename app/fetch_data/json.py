import pandas as pd
from pandas import json_normalize
from typing import Optional
from .config import *
from .thai_language_helper import parse_alien_language


def json_to_dataframe(data: dict) -> Optional[pd.DataFrame]:
    """
        แปลงข้อมูล(่json)เป็น Dataframe ที่ได้จากข้อมูลเหล่านั้น
        ในกรณีที่ไม่สามารถแปลงเป็น dataframe ไม่ได้ จะคืน None

    Args:
        data (dict): json ที่ได้จาก response

    Returns:
        pd.DataFrame: Dataframe ของข้อมูล  หรือ None
    """

    try:
        return json_normalize(data)
    except:
        return None


def get_json_response(r):
    """
     คืนค่า ข้อมูลในรูปของ dict ที่ได้จาก response

    Args:
        r (response): response ของที่ได้จากการเรียก request

    Returns:
        dict:  ข้อมูลในรูปของ json หรือ None
    """
    try: 
        return r.json()  # dict ,list 
    except:
        return None


def get_columns_json(df: pd.DataFrame) -> list:
    """
    คืนค่าลิสของฟิลด์(แถวแรกของข้อมูล) โดยที่แต่ละฟิลด์จะประกอบด้วยข้อมูลต่อไปนี้
        ชือฟิลด์
        ประเภทของข้อมูลในฟิลด์ 
        primary_key (เป็นค่า False เสมอ)
        ตัวอย่างข้อมูลในฟิลด์นั้น (ข้อมูลที่ได้แถวแรก)
        รายละเอียดของฟิลด์ (เป็น สติงว่าง เสมอ)

    Args:
        df (pd.DataFrame): pandas DataFrame Object.

    Returns:
        list: คืนค่าลิสของฟิลด์ หรือ ลิสว่าง
    """
    columns = list()
    column_names = df.columns.values.tolist()
    df_list = df.values.tolist()
    for column_name_index in range(df.shape[1]):
        first_row = df_list[0][column_name_index]
        column_name = column_names[column_name_index]
        d_type = df[column_name].dtype
        if d_type == list:
            if (type(first_row) == list):
                if (len(first_row) and (type(first_row[0]) in [list, object, dict])):
                    prefix = column_name+"."
                    new_df = json_normalize(first_row)
                    somethings = [{**s, "field": prefix+s["field"]}
                                  for s in get_columns_json(new_df)]
                    columns += (somethings)

                    continue
        column_data = {
            SCHEMA_FIELD_KEY: column_name,
            SCHEMA_TYPE_KEY:  type(first_row).__name__,
            SCHEMA_PRIMARY_KEY: False,
            SCHEMA_EXAMPLE_DATA_KEY:  first_row,
            SCHEMA_DESCRIPTION_KEY: ""
        }
        columns.append(column_data)
    return columns


def parse_to_json(r) -> tuple:
    """
    แปลงข้อมูลจาก response เป็น ฟิลด์ และจัดการกับข้อความภาษาไทย(ถ้ามี)ให้อยู่ในรูปแบบ utf

    Args:
        r (response): response ที่ได้จากการเรียก request

    Returns:
        tuple : ลิสของฟิลด์ ,  ข้อความของ response body  หลังจากจัดการกับภาษาไทยแล้ว , dict of list ของข้อมูล
    """
    text_data = parse_alien_language(r)
    text_data = text_data.replace("\'", "\"")
    data = get_json_response(r)
    schema = []
    if data :
        df = json_to_dataframe(data)
        if df is not None:
            schema = get_columns_json(df)
    return (schema, text_data, data)
