FROM python:3.11


COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app app
COPY entrypoint.sh app/
WORKDIR /app
RUN chmod a+x entrypoint.sh
RUN curl -L https://github.com/golang-migrate/migrate/releases/download/v4.17.1/migrate.linux-amd64.tar.gz | tar xvz

ENTRYPOINT ["./entrypoint.sh"]
