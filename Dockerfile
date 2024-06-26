FROM python:3.8.16

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt
COPY ./wsgi-service.py /code/wsgi-service.py 
COPY ./entrypoint.sh /code/entrypoint.sh

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app
COPY ./data /code/data
COPY ./manage.py /code/manage.py

ENTRYPOINT ["/code/entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "--host=0.0.0.0", "--port=80"]
