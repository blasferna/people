import urllib3
from zipfile import ZipFile

import requests
from bs4 import BeautifulSoup
from utils import insert_postgresql, create_table_postgresql, create_view_postgresql, file_compress

requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = 'ALL:@SECLEVEL=1'
BASE_URL = 'https://www.set.gov.py'
URL = f'{BASE_URL}/portal/PARAGUAY-SET/InformesPeriodicos?folder-id=repository:collaboration:/sites/PARAGUAY-SET/categories/SET/Informes%20Periodicos/listado-de-ruc-con-sus-equivalencias'

inserts = []

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
            "html.parser"
        )
        list_div = soup.select(".uiContentBox")[0]
        lits_rows = list_div.select(".media")
        for row in lits_rows:
            a = row.find('a')
            d = {}
            d[a['title']] = a['href']
            links.append(d)

        return links
    except requests.ConnectionError as e:
        print(f'Connection Error {e}')
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
            "html.parser"
        )
        div = soup.select(".detailContainer")[0]
        return div.select("a")[0]['href']
    except requests.ConnectionError as e:
        print(f'Connection Error {e}')
    except Exception as e:
        print(e)

    return None

def download(url, filename):
    r = requests.get(f"{BASE_URL}{url}", allow_redirects=True)
    location = f"tmp/{filename}"
    open(location, 'wb').write(r.content)
    return location

def extract(filename):
    with ZipFile(filename, 'r') as zipObj:
        zipObj.extractall('tmp')


def create_inserts(filename):
    with open(filename, 'r') as f:
        for line in f.readlines():
            try:
                ruc, rz, dv, str, d = line.split('|')
            except ValueError:
                ruc, rz, dv, str, d, d1 = line.split('|')
            inserts.append(insert_postgresql(ruc, rz, dv, str))

def build_database():
    with open('ruc.sql', 'w') as f:
        f.write(create_table_postgresql())
        f.write(create_view_postgresql())
        for insert in inserts:
            f.write(insert+"\n")

def zip_database():
    file_compress(['ruc.sql'], 'dist/ruc.zip')

if __name__ == '__main__':
    links = get_download_preview_links()
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
        print("Creatings inserts")
        create_inserts(f"tmp/{name.split('.')[0]}.txt")
    print("building database")
    build_database()
    zip_database()
