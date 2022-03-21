import requests
from .utils import encrypt_param

requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = "ALL:@SECLEVEL=1"


BASE_URL = "https://servicios.set.gov.py/eset-publico"
CITIZEN_URL = f"{BASE_URL}/ciudadano/recuperar"
TAXPAYER_URL = f"{BASE_URL}/contribuyente/estado"


class DoesNotExist(Exception):
    pass


def get_citizen(document):
    data = {"cedula": None, "apellidos": None, "nombres": None, "fecNac": None}
    session = requests.Session()
    response = session.request(
        "GET", CITIZEN_URL, params={"t3": encrypt_param(document, "cedula")}
    )
    if len(response.text) == 0:
        raise DoesNotExist("Not found")
    rjson = response.json()
    full_name = rjson["resultado"]["nombres"].rstrip()
    last_name = rjson["resultado"]["apellidoPaterno"].rstrip()
    mother_last_name = rjson["resultado"]["apellidoMaterno"].rstrip()

    data["cedula"] = rjson["resultado"]["cedula"]
    data["apellidos"] = f"{last_name} {mother_last_name}"
    data["nombres"] = full_name
    return data


def get_taxpayer(document):
    data = {
        "ruc": None,
        "razonsocial": None,
        "tipo": None,
        "categoria": 0,
        "dv": None,
        "fecNac": None,
    }
    session = requests.Session()
    response = session.request(
        "GET", TAXPAYER_URL, params={"t3": encrypt_param(document, "ruc")}
    )
    if len(response.text) == 0:
        citizen = get_citizen(document)
        if citizen:
            data["ruc"] = citizen["cedula"]
            data["razonsocial"] = f"{citizen['nombres']} {citizen['apellidos']}"
        else:
            raise DoesNotExist("Not found")
    else:
        rjson = response.json()
        data["ruc"] = rjson["ruc"]
        data["razonsocial"] = rjson["nombreCompleto"]
        data["dv"] = rjson["dv"]
    return data
