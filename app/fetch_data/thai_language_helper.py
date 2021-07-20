import codecs

def tis2utf(tis:str)-> str :
    """
    แปลงภาษาไทย จาก TIS620 to UTF


    Args:
        tis (str): ข้อความที่เป็น TIS620

    Returns:
        str: ข้อความที่เป็น UTF
    """

    
    s = ""
    for c in tis :
        if 0xa0 <= ord(c) <= 0xfb :
            s+= chr(ord(c) + 0xe00 - 0xa0)
        else :
            s+= c 
    return s 
def parse_alien_language(r) -> str:
    """
    แปลงภาษาไทย

    Args:
        r (response): response ที่ได้จากการเรียก request

    Returns:
        str: ข้อความที่เป็นภาษาไทยที่สามารถอ่านออกได้ ในแบบ UTF
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

