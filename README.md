# People

API que proporciona acceso a datos de contribuyentes del Paraguay. Este repositorio descarga de manera periódica la lista de contribuyentes proporcionada por la SET (Subsecretaría de Estado de Tributación) y construye una base de datos SQLite. Esta base de datos alimenta la API.

## Requisitos previos

Para ejecutar esta aplicación localmente, necesitarás tener instalado lo siguiente en tu sistema:

- Python 3.8 o superior
- Docker (Opcional)



## Configuración del entorno de desarrollo

1. Clona el repositorio en tu máquina local usando:

```bash
https://github.com/blasferna/people.git
```

2. Navega hasta el directorio del proyecto.
3. Crea un entorno virtual de Python (opcional, pero recomendado). Puedes hacerlo con el siguiente comando:

```bash
python -m venv env
```

3. Activa el entorno virtual. En Windows, usa `env\Scripts\activate`. En Unix o MacOS, usa `source env/bin/activate`.

4. Instala las dependencias necesarias con el siguiente comando:
```bash
pip install -r requirements.txt
```


## Ejecución local

Para ejecutar la aplicación localmente tienes dos opciones:

### Uvicorn

Uvicorn es un servidor ASGI ligero y rápido, construido sobre uvloop y httptools. Para ejecutar la aplicación con Uvicorn, sigue estos pasos:

1. Asegúrate de que estás en el directorio del proyecto.
2. Ejecuta el siguiente comando para iniciar el servidor Uvicorn:

```bash
uvicorn wsgi-service:app --reload
```

Este comando iniciará el servidor en `localhost` en el puerto `8000`. Puedes acceder a la aplicación en tu navegador web en `http://localhost:8000`.

### Docker

1. Construye la imagen de Docker con `docker build -t people .`.
2. Ejecuta la aplicación con `docker run --name people -p 80:80 people`.


## Uso del API

El API ofrece dos endpoints principales:

- **RUC**: Para obtener información sobre un RUC específico, realiza una solicitud GET a `https://127.0.0.1:8000/?ruc=<RUC>`.
- **IPS**: Para obtener información sobre un asegurado, realiza una solicitud GET a `https://127.0.0.1:5000/ips?documento=<documento>`. Lo que hace la app es scrappear la página de consulta asegurado y convertir el resultado en `JSON`.

## Despliegue

Para desplegar la aplicación en un entorno de producción, puedes utilizar la imagen de Docker disponible en `ghcr.io/blasferna/people:latest`.

Descargar:
```bash
docker pull ghcr.io/blasferna/people:latest
```
Ejecutar:
```bash
docker run --name people -p 80:80 ghcr.io/blasferna/people
```

