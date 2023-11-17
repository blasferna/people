# people
Api de datos de personas del Paraguay.

## Ruc

### Ejemplo

`Curl`
```bash
curl -X 'GET' \
  'https://peoplepy.herokuapp.com/?ruc=80009735' \
  -H 'accept: application/json'
```

`Url de la petición`
```
https://peoplepy.herokuapp.com/?ruc=80009735
```

`Respuesta`

```json
{
  "ruc": "80009735",
  "razonsocial": "ADMINISTRACION NACIONAL DE ELECTRICIDAD - ANDE",
  "tipo": "J",
  "categoria": "G",
  "dv": "1"
}
```

## IPS

### Ejemplo

`Curl`
```bash
curl -X 'GET' \
  'https://peoplepy.herokuapp.com/ips?documento=123456' \
  -H 'accept: application/json'
```

`Url de la petición`
```
https://peoplepy.herokuapp.com/ips?documento=123456
```

`Respuesta`

```json
{
    "Titular": {
        "Elegir": "", 
        "Nro Documento": "123456", 
        "Nombres": "JUAN", 
        "Apellidos": "PEREZ", 
        "Fecha Nacim": "26-11-1965", 
        "Sexo": "MASCULINO", 
        "Tipo Aseg.": "TITULAR", 
        "Beneficiarios Activos": "1", 
        "Enrolado": "NO", 
        "Vencimiento de fe de vida": ""
    }, 
    "Patronales": [
        {
            "Nro. Patronal": "00001-001-000111", 
            "Empleador": "NOMBRE DEL EMPLEADOR", 
            "Estado": "ACTIVO", 
            "Meses de aporte": "280", 
            "Vencimiento": "11-05-2022", 
            "Ultimo Periodo Abonado": "FEBRERO/2022"
        }
    ]
}
```
## Docker

### Construir localmente

```bash
docker build -t people .
```


Ejecutar localmente

```bash
docker run --name people -p 80:80 people
```

### Utilizar la version de `ghcr.io`

Descargar

```bash
docker pull ghcr.io/blasferna/people:latest
```

Ejecutar

```bash
docker run --name people -p 80:80 ghcr.io/blasferna/people
```
