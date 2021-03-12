
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
