import base64
import csv
import json
import typing
import zipfile
from datetime import datetime

import requests
from Crypto.Cipher import AES
from Crypto.Util import Padding
from starlette.responses import Response
from tqdm import tqdm


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


def str_to_datestr(value):
    return datetime.strptime(value, "%Y-%m-%d").strftime("%d/%m/%Y")


def encrypt_param(param, variant="ruc"):
    encryption_key = base64.b64decode("aCIbjMuVGtwF8nlSKoPydE==")
    text = json.dumps({variant: param}).encode()
    text_padded = Padding.pad(text, AES.block_size)
    iv = base64.b64decode("JAwlt7SNbYLycmPRqeDFou==")
    cipher = AES.new(encryption_key, AES.MODE_CBC, iv)
    cipher_enc = cipher.encrypt(text_padded)
    return base64.b64encode(cipher_enc).decode()


def get_delimitter(buffer):
    try:
        dialect = csv.Sniffer().sniff(buffer.readline(), delimiters=";,")
        return dialect.delimiter
    except csv.Error:
        return "\t"


def insert_values(ruc, razon_social, dv, ruc_str):
    razon_social = razon_social.replace("'", "''")
    ruc_str = ruc_str.replace("'", "''").replace(chr(92), "")
    return f"""('{ruc}', '{razon_social}', '{dv}', '{ruc_str}')"""


def file_compress(inp_file_names, out_zip_file):
    """
    function : file_compress
    args : inp_file_names : list of filenames to be zipped
    out_zip_file : output zip file
    return : none
    assumption : Input file paths and this code is in same directory.
    """
    # Select the compression mode ZIP_DEFLATED for compression
    # or zipfile.ZIP_STORED to just store the file
    compression = zipfile.ZIP_DEFLATED
    print(f" *** Input File name passed for zipping - {inp_file_names}")

    # create the zip file first parameter path/name, second mode
    print(f" *** out_zip_file is - {out_zip_file}")
    zf = zipfile.ZipFile(out_zip_file, mode="w")

    try:
        for file_to_write in inp_file_names:
            # Add file to the zip file
            # first parameter file to zip, second filename in zip
            print(f" *** Processing file {file_to_write}")
            zf.write(file_to_write, file_to_write, compress_type=compression)
    except FileNotFoundError as e:
        print(f" *** Exception occurred during zip process - {e}")
    finally:
        # Don't forget to close the file!
        zf.close()


def download(url, dest_path):
    response = requests.get(url, stream=True, allow_redirects=True)
    total_size = int(response.headers.get('content-length', 0))
    with open(dest_path, 'wb') as file, tqdm(
        desc=dest_path,
        total=total_size,
        unit='B',
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for data in response.iter_content(chunk_size=1024):
            size = file.write(data)
            bar.update(size)
