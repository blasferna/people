import glob
import os
import sqlite3
from zipfile import ZipFile

import pandas as pd
import requests
from bs4 import BeautifulSoup

from utils import (
    create_table_postgresql,
    create_view_postgresql,
    file_compress,
    insert_postgresql,
    insert_values,
)

requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = "ALL:@SECLEVEL=1"
BASE_URL = "https://www.set.gov.py"
URL = f"{BASE_URL}/portal/PARAGUAY-SET/InformesPeriodicos?folder-id=repository:collaboration:/sites/PARAGUAY-SET/categories/SET/Informes%20Periodicos/listado-de-ruc-con-sus-equivalencias"
URL_PERSONAS_JURIDICAS = f"{BASE_URL}/portal/PARAGUAY-SET/InformesPeriodicos?folder-id=repository:collaboration:/sites/PARAGUAY-SET/categories/SET/Informes%20Periodicos/lista-de-contribuyentes-que-son-personas-juridicas"

values = []
values_list = []
pj = {}


def get_download_preview_links():
    links = []
    try:
        soup = BeautifulSoup(
            requests.get(
                URL,
                timeout=10,
                headers={"user-agent": "Mozilla/5.0"},
                verify=True,
            ).text,
            "html.parser",
        )
        list_div = soup.select(".uiContentBox")[0]
        lits_rows = list_div.select(".media")
        for row in lits_rows:
            a = row.find("a")
            d = {}
            d[a["title"]] = a["href"]
            links.append(d)

        return links
    except requests.ConnectionError as e:
        print(f"Connection Error {e}")
    except Exception as e:
        print(e)

    return None


def get_download_link(url):
    link = None
    try:
        soup = BeautifulSoup(
            requests.get(
                f"{BASE_URL}{url}",
                timeout=10,
                headers={"user-agent": "Mozilla/5.0"},
                verify=True,
            ).text,
            "html.parser",
        )
        div = soup.select(".detailContainer")[0]
        return div.select("a")[0]["href"]
    except requests.ConnectionError as e:
        print(f"Connection Error {e}")
    except Exception as e:
        print(e)

    return None


def get_personas_juridicas_link():
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
        list_div = soup.select(".media-body")[0]
        download_page_url = list_div.select("a")[0]["href"]

        soup = BeautifulSoup(
            requests.get(
                f"{BASE_URL}{download_page_url}",
                timeout=10,
                headers={"user-agent": "Mozilla/5.0"},
                verify=True,
            ).text,
            "html.parser",
        )
        return soup.select(".btn-primary")[0]["href"]
    except requests.ConnectionError as e:
        print(f"Connection Error {e}")
    except Exception as e:
        print(e)

    return None


def extract_pj():
    """
        Column Index:
        0 = RUC                        
        1 = DV                         
        2 = NOMBRE_RAZON_SOCIAL        
        3 = CATEGORIA                  
    """

    def _categoria(value):
        return "P" if value == "PEQUENO" else "M" if value == "MEDIANO" else "G"

    os.system("cd tmp && unrar e juridicas.rar -y")
    path = os.getcwd()
    path = os.path.join(path, "tmp")
    csv_files = glob.glob(os.path.join(path, "*.xlsx"))
    for f in csv_files:
        df = pd.read_excel(f, header=None)
        for index, row in df.iterrows():
            if row[0] != "NaN":
                pj[f"{row[0]}-{row[1]}"] = _categoria(row[3])


def download(url, filename):
    r = requests.get(f"{BASE_URL}{url}", allow_redirects=True)
    location = f"tmp/{filename}"
    open(location, "wb").write(r.content)
    return location


def extract(filename):
    with ZipFile(filename, "r") as zipObj:
        zipObj.extractall("tmp")


def create_values(filename):
    with open(filename, "r", encoding="utf8") as f:
        for line in f.readlines():
            try:
                ruc, rz, dv, str, status, d1 = line.split("|")
            except ValueError:
                ls = [x for x in line.split("|") if len(x) > 0 and x != "\n"]
                if len(ls) == 5:
                    ruc, rz, dv, str, status = ls
            rz = rz.replace(",", "")
            values.append(insert_values(ruc, rz, dv, str))
            cat = pj.get(f"{ruc}-{dv}", False)
            tipo = "F" if not cat else "J"
            values_list.append((ruc, rz, tipo, cat, dv, status))


def build_database():
    with open("ruc.sql", "w", encoding="utf8") as f:
        f.write(create_table_postgresql())
        f.write(create_view_postgresql())

        chunks = [values[x : x + 1000] for x in range(0, len(values), 1000)]
        for v in chunks:
            f.write("\n" + insert_postgresql(",\n".join(v)))


def build_sqlite3():
    con = sqlite3.connect("ruc.db")
    cur = con.cursor()
    cur.execute("DROP TABLE ruc")
    cur.execute(
        """CREATE TABLE ruc
                (ruc text, razonsocial text, tipo text, categoria text, dv text, estado text)"""
    )

    cur.executemany("INSERT INTO ruc VALUES (?, ?, ?, ?, ?, ?)", values_list)
    con.commit()
    con.close()


def zip_database():
    file_compress(["ruc.sql"], "../dist/ruc.zip")


if __name__ == "__main__":
    print("getting links")
    links = get_download_preview_links()
    # pj
    print("downloading juridicas.rar")
    download(get_personas_juridicas_link(), "juridicas.rar")
    print("extracting juridicas.rar")
    extract_pj()

    for d in links:
        name = list(d.keys())[0]
        url = d[name]
        print(f"downloading {name}")
        dl = get_download_link(url)
        filename = download(dl, name)
        try:
            extract(filename)
        finally:
            print(f"{filename} extracted")
        print("building values")
        create_values(f"tmp/{name.split('.')[0]}.txt")
    print("building database")
    build_database()
    print("building sqlite database")
    build_sqlite3()
    zip_database()
