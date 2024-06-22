# People

En la primera ejecución, la aplicación descarga los archivos de RUCs y equivalencias de la DNIT y construye una base de datos SQLite. Luego, levanta un servidor con una API REST para consultar los datos.

## Configuración del Entorno de Desarrollo

1. Clona el repositorio del proyecto.

```bash
git clone https://github.com/blasferna/people.git
```

2. Navega al directorio del proyecto:
    
```bash
cd people
```

3. Crea y activa un entorno virtual de Python:

```bash
python -m venv env
source env/bin/activate  # En Windows: env\Scripts\activate
```

4. Instala las dependencias del proyecto:

```bash
pip install -r requirements.txt
```

## Ejecución Local

1. Asegúrate de tener el entorno virtual activado.
2. Ejecuta el servidor web con el siguiente comando:

```bash
python manage.py runserver
```

El servidor estará disponible en `http://127.0.0.1:3000`.

> [!NOTE]
> Si es la primera vez que ejecutas el servidor, la aplicación descargará los archivos de RUCs y equivalencias de la DNIT y construirá la base de datos SQLite. Este proceso puede tardar varios minutos.

## Comandos CLI

El proyecto incluye varios comandos CLI para gestionar diferentes tareas:

- `python manage.py runserver`: Ejecuta el servidor web.
- `python manage.py build`: Vuelve a construir la base de datos. Descarga los archivos de RUCs y equivalencias y reconstruye la base de datos SQLite.
- `python manage.py download`: Descarga bases de datos preconstruidas desde URLs especificadas en las variables de entorno (opcional).
  - `RUC_DB_URL`: URL de la base de datos de RUCs preconstruida.
  - `PEOPLE_DB_URL`: URL de la base de datos de personas preconstruida.

## Despliegue

### Docker

El proyecto se puede desplegar utilizando Docker. La imagen está alojada en el registro de GitHub:

```bash
docker pull ghcr.io/blasferna/people:latest
```

Es necesario crear un volumen para almacenar los datos:

```bash
docker volume create people_data
```

Ejecuta la imagen con el siguiente comando:

```bash
docker run --name people -p 80:80 -v people_data:/code ghcr.io/blasferna/people
```

Opcionalmente puedes ejecutar los comandos CLI de la aplicación utilizando Docker. Por ejemplo, para reconstruir la base de datos:

```bash
docker run -v people_data:/code ghcr.io/blasferna/people build
```

### Docker Compose

También puedes utilizar Docker Compose para desplegar la aplicación. Asegúrate de crear un archivo `docker-compose.yml` con el siguiente contenido:

```yaml
version: '3'

services:
  app:
    image: ghcr.io/blasferna/people:latest
    ports:
      - "80:80"
    volumes:
      - people_data:/code
    restart: unless-stopped

volumes:
  people_data:
```

En este caso, no es necesario construir la imagen localmente, ya que se utilizará la imagen `ghcr.io/blasferna/people:latest` del registro de GitHub.

Para desplegar la aplicación con Docker Compose, ejecuta el siguiente comando:

```bash
docker-compose up -d
```

Este comando descargará la imagen del registro de GitHub, creará un volumen llamado `people_data` para almacenar los datos persistentes, y ejecutará el contenedor en segundo plano.

La opción `-d` indica que el contenedor se ejecutará en segundo plano y en combinación con la opción `restart: unless-stopped` del archivo `docker-compose.yml`, el contenedor se reiniciará automáticamente si se detiene o se reinicia el sistema.


Para detener:

```bash
docker-compose stop
```

Para detener y eliminar los contenedores:

```bash
docker-compose down -v
```

La opción `-v` eliminará el volumen `people_data` junto con los contenedores. Sólo ejecutar cuando se desee eliminar los datos almacenados.

## Endpoints

### Obtener datos de RUC por número

```bash
curl -X 'GET' \
  'http://127.0.0.1:3000/?ruc=80009735' \
  -H 'accept: application/json'
```

Respuesta:

```json
{
  "ruc": "80009735",
  "razonsocial": "ADMINISTRACION NACIONAL DE ELECTRICIDAD - ANDE",
  "tipo": "J",
  "categoria": "GRANDE",
  "dv": "1",
  "estado": "ACTIVO"
}
```

### Búsqueda por número de RUC o nombre de contribuyente

```bash
curl -X 'GET' \
  'http://127.0.0.1:3000/search?query=80009735' \
  -H 'accept: application/json'
```

Respuesta:

```json
[
  {
    "ruc": "80009735",
    "razonsocial": "ADMINISTRACION NACIONAL DE ELECTRICIDAD - ANDE",
    "tipo": "J",
    "categoria": "GRANDE",
    "dv": "1",
    "estado": "ACTIVO"
  }
]
```
