import pandas as pd
from io import StringIO
from typing import Optional

from .config import *
from .thai_language_helper import parse_alien_language


def string_to_dataframe(text: str)-> Optional[pd.DataFrame]:
    """
        แปลงข้อมูลในรูปแบบของ string ให้เป็น DataFrame

    Args:
        text (str): ข้อมูลในรูปแบบของ string

    Returns:
        pd.DataFrame: Dataframe ของข้อมูล หรือ None
    """
    try:
        text_data = StringIO(text)
        return pd.read_csv(text_data)
    except:
        return None


def get_columns_csv(df: pd.DataFrame) -> list:
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
        column_data = {
            SCHEMA_FIELD_KEY: column_names[column_name_index],
            SCHEMA_TYPE_KEY:  type(first_row).__name__,
            SCHEMA_PRIMARY_KEY: False,
            SCHEMA_EXAMPLE_DATA_KEY: first_row,
            SCHEMA_DESCRIPTION_KEY: ""
        }
        columns.append(column_data)
    return columns

def dataframe_to_list(df: pd.DataFrame) ->list:
    """
    Convert DataFrame to List
        - List[0] : Field,Column header,Dimension
        - List[1 to n] : Row , list of data for each column
    Args:
        df (pd.DataFrame): DataFrame

    Returns:
        list: List of Dataframe
    """
    return [df.columns.values.tolist()] + df.values.tolist()

def parse_to_csv(r) -> tuple:
    """
    แปลงข้อมูลจาก response เป็น ฟิลด์ และจัดการกับข้อความภาษาไทย(ถ้ามี)ให้อยู่ในรูปแบบ utf

    Args:
        r (response): response ที่ได้จากการเรียก request

    Returns:
        tuple : ลิสของฟิลด์ ,  ข้อความของ response body  หลังจากจัดการกับภาษาไทยแล้ว, list ของข้อมูล
    """
 

    text_data = parse_alien_language(r)
    df = string_to_dataframe(text_data)
    if df is not None:
        schema = get_columns_csv(df)
        df_list = dataframe_to_list(df)
    return (schema, text_data,df_list)
