# people
Api de datos de personas del Paraguay.

## Ruc

### Ejemplo

`Curl`
```bash
curl -X 'GET' \
  'https://peoplepy.herokuapp.com/?ruc=5049813-4' \
  -H 'accept: application/json'
```

`Url de la petición`
```
https://peoplepy.herokuapp.com/?ruc=5049813-4
```

`Respuesta`

```json
{
  "ruc": "5049813-4",
  "razonsocial": "FERNANDEZ CACERES, BLAS ISAIAS"
}
```

## IPS

### Ejemplo

`Curl`
```bash
curl -X 'GET' \
  'https://peoplepy.herokuapp.com/ips?documento=5049813' \
  -H 'accept: application/json'
```

`Url de la petición`
```
https://peoplepy.herokuapp.com/ips?documento=5049813
```

`Respuesta`

```json
{
  "Titular": {
    "Elegir": "",
    "Nro Documento": "5049813",
    "Nombres": "BLAS ISAIAS",
    "Apellidos": "FERNANDEZ CACERES",
    "Fecha Nacim": "15-04-1991",
    "Sexo": "MASCULINO",
    "Tipo Aseg.": "TITULAR",
    "Beneficiarios Activos": "3",
    "Enrolado": "SI",
    "Vencimiento de fe de vida": ""
  },
  "Patronales": [
    {
      "Nro. Patronal": "0291-61-00040",
      "Empleador": "COMPY CENTER S.A.",
      "Estado": "ACTIVO",
      "Meses de aporte": "42",
      "Vencimiento": "14-02-2022",
      "Ultimo Periodo Abonado": "NOVIEMBRE/2021"
    }
  ]
}
```
## Docker

Contruir localmente

```bash
docker build -t api .
```


Ejecutar localmente

```bash
docker run --name api -p 80:80 api
```

## Roadmap
* <s>Base de datos de RUC auto actualizado.</s>
* Base de datos de personas basado en el padrón nacional.
