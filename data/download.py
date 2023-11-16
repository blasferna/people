import glob
import os
import sqlite3
from zipfile import ZipFile

import requests
import tabula
from bs4 import BeautifulSoup
from utils import insert_values

requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = "ALL:@SECLEVEL=1"
BASE_URL = "https://www.set.gov.py"
URL_RUCS = f"{BASE_URL}/web/portal-institucional/listado-de-ruc-con-sus-equivalencias"
URL_PERSONAS_JURIDICAS = (
    f"{BASE_URL}/web/portal-institucional/contribuyentes-que-son-personas-jurídicas"
)

values = []
values_list = []
pj = {}


def get_ruc_download_links():
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


def get_personas_juridicas_link():
    link = None
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


def extract_pj():
    def _category(value):
        if value == "PEQUENO":
            return "P"
        elif value == "MEDIANO":
            return "M"
        elif value == "GRANDE":
            return "G"
        else:
            return "D"

    path = os.getcwd()
    path = os.path.join(path, "tmp")
    csv_files = glob.glob(os.path.join(path, "*.pdf"))

    for f in csv_files:
        dfs = tabula.read_pdf(f, pages="all", multiple_tables=True)
        for df in dfs:
            for index, row in df.iterrows():
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
                pj[f"{ruc}-{dv}"] = _category(category)


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


def build_sqlite3():
    con = sqlite3.connect("ruc.db")
    cur = con.cursor()
    cur.execute("DROP TABLE IF EXISTS ruc")
    cur.execute(
        """CREATE TABLE ruc
                (ruc text, razonsocial text, tipo text, categoria text, dv text, estado text)"""
    )

    cur.executemany("INSERT INTO ruc VALUES (?, ?, ?, ?, ?, ?)", values_list)
    con.commit()
    con.close()


def update_counter():
    con = sqlite3.connect("ruc.db")
    cur = con.cursor()
    cur.execute("SELECT count(*) as count FROM ruc")
    data = cur.fetchone()
    if data:
        with open("../counter.txt", "w") as f:
            f.write(str(data[0]))


if __name__ == "__main__":
    print("getting links")
    links = get_ruc_download_links()
    # pj
    print("downloading listado de personas juridicas")
    download(get_personas_juridicas_link(), "personas-juridicas.pdf")
    print("extracting listado de personas juridicas")
    extract_pj()

    for d in links:
        name = list(d.keys())[0]
        url = d[name]
        print(f"downloading {name}")
        filename = download(url, name)
        try:
            extract(filename)
        finally:
            print(f"{filename} extracted")
        print("building values")
        create_values(f"tmp/{name.split('.')[0]}.txt")
    print("building sqlite database")
    build_sqlite3()
    print("updating counter")
    update_counter()
