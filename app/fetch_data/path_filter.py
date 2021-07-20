
def field_path_filter(data :  list,path : str) ->  list :
    """
    กรอง schema ตาม path ที่ได้รับ
    Args:
        data (list): list ของ schema
        path (str): path ของฟิลด์ทั้งหมดที่ต้องการให้คืนค่า ในกรณีที่ต้องการให้คืนค่าฟิลด์ที่อยู่ซ้อนกันให้คั่นด้วยจุด(.)

    Returns:
        list: list ของ schema ที่ได้จาก path ดังกล่าว
    """
  
    if path and path.strip():
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
    กรองข้อมูล (่json) ตาม path ที่ได้รับ

    Args:
        data (list): json ของ ข้อมูลทั้งหมด
        path (str): path ของฟิลด์ทั้งหมดที่ต้องการให้คืนค่า ในกรณีที่ต้องการให้คืนค่าฟิลด์ที่อยู่ซ้อนกันให้คั่นด้วยจุด(.)

    Returns:
        json : ข้อมูลที่อยู่ใน path ดังกล่าว
    """

   
    data_pool  = [data]
    json_data = None
    if path and path.strip():
        path_list = path.split('.')
        for key_index in range(len(path_list)) :
            key = path_list[key_index]
            if type(data_pool[key_index]) is dict :
                if  key in data_pool[key_index] : 

                    temp = data_pool[key_index][key]
                    data_pool.append(temp) 
                    json_data = temp
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
