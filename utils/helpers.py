import base64

from fastapi import HTTPException

def decode_photo(path,encoded_string):
    with open(path,'w+b') as f:
        try:
            f.write(base64.b64decode(encoded_string.encode("utf-8"))) 
        except Exception as err:
            raise HTTPException(400,"Invalid photo encoding")