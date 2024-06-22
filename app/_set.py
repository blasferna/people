import glob
import os
import sqlite3
import uuid
from zipfile import ZipFile

import pandas as pd
import requests
import tabula
from bs4 import BeautifulSoup

from .utils import download, encrypt_param, insert_values

requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = "ALL:@SECLEVEL=1"

BASE_URL_SET = "https://www.set.gov.py"
BASE_URL_SERVICES = "https://servicios.set.gov.py/eset-publico"
URL_RUCS = (
    f"{BASE_URL_SET}/web/portal-institucional/listado-de-ruc-con-sus-equivalencias"
)
URL_PERSONAS_JURIDICAS = (
    f"{BASE_URL_SET}/web/portal-institucional/contribuyentes-que-son-personas-jurídicas"
)
CITIZEN_URL = f"{BASE_URL_SERVICES}/ciudadano/recuperar"
TAXPAYER_URL = f"{BASE_URL_SERVICES}/contribuyente/estado"


class DoesNotExist(Exception):
    pass


def get_citizen(document):
    data = {"cedula": None, "apellidos": None, "nombres": None, "fecNac": None}
    session = requests.Session()
    response = session.request(
        "GET",
        CITIZEN_URL,
        params={"t3": encrypt_param(document, "cedula")},
        timeout=(5, 5),
    )
    if len(response.text) == 0:
        raise DoesNotExist("Not found")
    rjson = response.json()
    full_name = rjson["resultado"]["nombres"].rstrip()
    last_name = rjson["resultado"]["apellidoPaterno"].rstrip()
    mother_last_name = ""
    if rjson["resultado"]["apellidoMaterno"] is not None:
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
        "GET",
        TAXPAYER_URL,
        params={"t3": encrypt_param(document, "ruc")},
        timeout=(5, 5),
    )
    if len(response.text) == 0:
        citizen = get_citizen(document)
        if citizen:
            data["ruc"] = citizen["cedula"]
            data["razonsocial"] = f"{citizen['apellidos']} {citizen['nombres']}"
        else:
            raise DoesNotExist("Not found")
    else:
        rjson = response.json()
        data["ruc"] = rjson["ruc"]
        data["razonsocial"] = rjson["nombreCompleto"]
        data["dv"] = rjson["dv"]
    return data


class RucCrawler:
    def __init__(self, database="data/ruc.db"):
        self.database = database
        self.files = []
        self.links = self.get_links()

    def get_links(self):
        links = []
        try:
            soup = BeautifulSoup(
                requests.get(
                    URL_RUCS,
                    timeout=10,
                    headers={"user-agent": "Mozilla/5.0"},
                    verify=True,
                ).text,
                "html.parser",
            )
            items = soup.find_all("div", class_="list__item search-item")
            for item in items:
                title = item.find("h3", class_="item__title").text.strip()
                download_link = item.find("a", class_="link")["href"]
                links.append({title: download_link})
        except requests.ConnectionError as e:
            print(f"Connection Error {e}")
        except Exception as e:
            print(e)

        return links

    def download(self):
        for link in self.links:
            name = list(link.keys())[0]
            url = link[name]
            local_filename = f"data/tmp/{name}"
            download(f"{BASE_URL_SET}{url}", local_filename)
            try:
                with ZipFile(local_filename, "r") as zip_ref:
                    zip_ref.extractall("data/tmp")
            finally:
                print(f"{name} extracted")
            self.files.append(f"data/tmp/{name.split('.')[0]}.txt")
            print(f"Deleting file {local_filename}...")
            os.remove(local_filename)

    def save(self, personas_juridicas=None):
        print("Saving...")
        values = []
        values_list = []
        for filename in self.files:
            with open(filename, "r", encoding="utf8") as f:
                for line in f.readlines():
                    try:
                        ruc, rz, dv, _str, status, d1 = line.split("|")
                    except ValueError:
                        ls = [x for x in line.split("|") if len(x) > 0 and x != "\n"]
                        if len(ls) == 5:
                            ruc, rz, dv, _str, status = ls
                    rz = rz.replace(",", "")
                    values.append(insert_values(ruc, rz, dv, _str))
                    tipo = "F"
                    cat = ""
                    if personas_juridicas:
                        persona_juridica = personas_juridicas.get(str(ruc))
                        if persona_juridica:
                            tipo = "J"
                            cat = persona_juridica["category"]
                    values_list.append((ruc, rz, tipo, cat, dv, status))

            print(f"Deleting file {filename}...")
            os.remove(filename)

        conn = sqlite3.connect(self.database)
        cur = conn.cursor()
        cur.execute("DROP TABLE IF EXISTS ruc")
        cur.execute(
            """
            CREATE TABLE ruc
            (
                ruc         TEXT,
                razonsocial TEXT,
                tipo        TEXT,
                categoria   TEXT,
                dv          TEXT,
                estado      TEXT
            ) 
            """
        )
        cur.execute("CREATE INDEX ruc_index ON ruc (ruc)")
        cur.executemany("INSERT INTO ruc VALUES (?, ?, ?, ?, ?, ?)", values_list)
        conn.commit()
        conn.close()

    def run(self, crawl_personas_juridicas=True):
        personas_juridicas = None
        if crawl_personas_juridicas:
            personas_juridicas = PersonasJuridicasCrawler(self.database)
            personas_juridicas.run(save=False)
            personas_juridicas = personas_juridicas.people
        self.download()
        self.save(personas_juridicas)


class PersonasJuridicasCrawler:
    def __init__(self, database="data/ruc.db"):
        self.database = database
        self.people = {}
        self.file = None
        self.link = self.get_link()

    def get_link(self):
        try:
            soup = BeautifulSoup(
                requests.get(
                    URL_PERSONAS_JURIDICAS,
                    timeout=10,
                    headers={"user-agent": "Mozilla/5.0"},
                    verify=True,
                ).text,
                "html.parser",
            )
            items = soup.find_all("div", class_="list__item search-item")
            for item in items:
                if item.attrs["data-value"] == "2022":
                    continue
                link = item.find("a", class_="link", attrs={"download": ""})["href"]
        except requests.ConnectionError as e:
            print(f"Connection Error {e}")
        except Exception as e:
            print(e)

        return link

    def download(self):
        local_filename = f"data/tmp/{self.link.split('/')[-1]}"
        download(f"{BASE_URL_SET}{self.link}", local_filename)
        self.file = local_filename

    def get_category(self, value):
        if value == "PEQUENO":
            return "P"
        elif value == "MEDIANO":
            return "M"
        elif value == "GRANDE":
            return "G"
        else:
            return "D"

    def extract(self):
        print(f"Extracting {self.file}...")

        try:
            with ZipFile(self.file, "r") as zip_ref:
                zip_ref.extractall("data/tmp")
        except Exception as e:
            print(e)
        finally:
            print(f"{self.file} extracted")

        path = os.path.join(os.getcwd(), "data")
        path = os.path.join(path, "tmp")
        files = glob.glob(os.path.join(path, "*.pdf"))
        files += glob.glob(os.path.join(path, "*.xlsx"))
        files += glob.glob(os.path.join(path, "*.xls"))

        for f in files:
            if f.endswith(".pdf"):
                print(f"Processing {f}...")
                dfs = tabula.read_pdf(f, pages="all", multiple_tables=True)
                for df in dfs:
                    self.process_dataframe(df)
            if f.endswith(".xlsx") or f.endswith(".xls"):
                print(f"Processing {f}...")
                df = pd.read_excel(f)
                self.process_dataframe(df)

            print(f"Deleting file {f}...")
            os.remove(f)
        print(f"Deleting file {self.file}...")
        os.remove(self.file)

    def process_dataframe(self, df):
        for index, row in df.iterrows():
            if row[0] == "NaN":
                continue
            try:
                ruc = row[0]
                dv = row[1]
                category = row[3]
            except IndexError:
                ruc = row[0]
                dv = row[1]
                if row[2].endswith("PEQUENO"):
                    category = "PEQUENO"
                elif row[2].endswith("MEDIANO"):
                    category = "MEDIANO"
                elif row[2].endswith("GRANDE"):
                    category = "GRANDE"
                else:
                    category = "DESCONOCIDO"
                category = self.get_category(category)
            self.people[str(ruc)] = {"ruc": ruc, "dv": dv, "category": category}

    def save(self):
        print("Saving...")
        table_name = "pj_" + uuid.uuid4().hex
        conn = sqlite3.connect(self.database)
        cur = conn.cursor()
        print(f"Creating temporary table {table_name}...")
        cur.execute(
            f"""
            CREATE TABLE {table_name}
            (
                ruc         TEXT,
                dv          TEXT,
                categoria   TEXT
            ) 
            """
        )
        values = []
        for ruc, data in self.people.items():
            values.append((data["ruc"], data["dv"], data["category"]))

        print(f"Inserting {len(values)} records...")
        cur.executemany(f"INSERT INTO {table_name} VALUES (?, ?, ?)", values)
        conn.commit()

        print("Updating ruc table...")
        cur.execute(
            f"""
            UPDATE ruc
            SET categoria = (
                SELECT categoria
                FROM {table_name}
                WHERE ruc = ruc.ruc
            ),
            tipo = 'J'
            WHERE ruc IN (
                SELECT ruc
                FROM {table_name}
            )
            """
        )
        conn.commit()

        print(f"Dropping table {table_name}...")
        cur.execute(f"DROP TABLE {table_name}")

        conn.close()

    def run(self, save=True):
        self.download()
        self.extract()
        if save:
            self.save()
