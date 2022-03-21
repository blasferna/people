import base64
import json
import typing
from datetime import datetime, timedelta

from Crypto.Cipher import AES
from Crypto.Util import Padding
from starlette.responses import Response


class PrettyJSONResponse(Response):
    media_type = "application/json"

    def render(self, content: typing.Any) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=4,
            separators=(", ", ": "),
        ).encode("utf-8")


def int_to_datestr(value):
    s = str(value)
    fecnac = datetime(year=int(s[0:4]), month=int(s[4:6]), day=int(s[6:8]))
    return fecnac.strftime("%d/%m/%Y")


def encrypt_param(param, variant="ruc"):
    encryption_key = base64.b64decode("aCIbjMuVGtwF8nlSKoPydE==")
    text = json.dumps({variant: param}).encode()
    text_padded = Padding.pad(text, AES.block_size)
    iv = base64.b64decode("JAwlt7SNbYLycmPRqeDFou==")
    cipher = AES.new(encryption_key, AES.MODE_CBC, iv)
    cipher_enc = cipher.encrypt(text_padded)
    return base64.b64encode(cipher_enc).decode()
