FROM python:3.11

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app
COPY ./certs /code/certs
COPY .env /code/.env
COPY .htpasswd /code/.htpasswd

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "443", "--ssl-keyfile=/code/certs/privkey.pem", "--ssl-certfile=/code/certs/fullchain.pem"]