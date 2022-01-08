import requests

from bs4 import BeautifulSoup

class IPSException(Exception):
    pass 

def consulta_asegurado(nro_cic):

    def clean_data(data):
        return data.get_text().replace('\n', '').replace('\t', '').strip()
        
    url = 'https://servicios.ips.gov.py/consulta_asegurado/comprobacion_de_derecho_externo.php'
    form_data = {'nro_cic': str(nro_cic), 'recuperar': 'Recuperar', 'elegir': '', 'envio':'ok'}
    session = requests.Session()
    try:
        soup = BeautifulSoup(
            session.post(
                url, 
                data=form_data,
                timeout=10,
                headers={'user-agent': 'Mozilla/5.0'},
                verify=True
            ).text, 
            "html.parser"
        )
        
        table = soup.select('form > table')[1]
        head = table.select('th')
        data_row = table.select('td')
        titular = dict(zip(map(clean_data, head), map(clean_data,data_row)))

        table = soup.select('form > table')[2]
        head = table.select('th')
        data_row = table.select('tr')

        patronales = []
        for i in range(1, len(data_row)):
            patronales.append(dict(zip(map(clean_data, head), map(clean_data,data_row[i].select('td')))))

        return {
            "Titular": titular,
            "Patronales": patronales
        }
        
    except requests.ConnectionError:
        raise IPSException("Connection Error")
    except Exception as e:
        IPSException(str(e))
