from base64 import b64encode

from fastapi import HTTPException


def decode_photo(path, encoded_string):
    print("path", path)
    with open(path, "wb") as f:
        try:
            _obj = encoded_string.encode("utf-8")
            f.write(b64encode(_obj))
        except Exception as err:
            raise HTTPException(400, "Invalid photo encoding")
