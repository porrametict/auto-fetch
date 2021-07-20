### การใช้งาน ! WANT UPDATE !!
โดยทั่วไปสามารถได้รับข้อมูลของ JSON และ CSV โดยผ่านค่า ของ url ลงไปในฟังก์ชัน ```get_data ``` หรือกรณีที่ต้องการข้อมูลเฉพาะบางฟิลด์ สามารถใช้งาน โดยการผ่านค่าฟิลด์ที่ต้องการลงใน path_filter
```
from .easy_func import get_data
url = "https://jsonplaceholder.typicode.com/users"

data = get_data(url=url)

# path filter
path = "address"
data = get_data(url=url,path_filter=path)
```

เมื่อฟังก์ชันทำงานสำเร็จ จะคืนค่าเป็น dict โดยมี key ดังต่อไปนี้
1. response_status(integer) HTTP status code
2. format(string) ชนิดของข้อมูลที่ได้รับจากการดึงข้อมูลที่ได้จาก url
3. text_data(string) ข้อมูลที่ได้รับ
4. schema(list) ลิตส์ของ field ที่ได้จากข้อมูล
5. schema_json(list) dict ของ ลิตส์ของ field 
6. pure_schema(list) ลิตส์ของ field ที่ได้จากข้อมูล(กรณีที่การ ผ่านค่า path_filter ข้อมูลนี้จะเป็นข้อมูลตั้งต้นที่จะไม่ได้รับผลกระทบ)

* กรณีข้อมูลเป็น JSON
7. pretty_data(string) = ข้อมูลเดียวกับ text_data แต่จะเป็นข้อมูลที่ได้รับผลกระทบจาก การผ่านค่า path_filter

* กรณีข้อมูลเป็น CSV
7. csv_items(list) ลิตส์ของข้อมูลในแต่ละแถว
8. csv_headers(list) ลิตส์ของชื่อฟิวส์ในแต่ละคอลัมน์

ข้อควรระวัง การผ่านค่า path_filter ใช้งานได้เฉพาะข้อมูลที่เป็น JSON เท่านั้น