import psycopg
from flask import g

class DBConnector:
    def __init__(self, app):
        self.app = app
        self.app.teardown_appcontext(self.disconnect)

    def get_dsn(self):
        dsn = "dbname={} user={} password={} host={} port={}".format(self.app.config["DB_NAME"],
                                                                     self.app.config["DB_USER"],
                                                                     self.app.config["DB_PASSWORD"],
                                                                     self.app.config["DB_HOST"],
                                                                     self.app.config["DB_PORT"])
        self.app.logger.info(dsn)
        return dsn

    def connect(self):
        if 'db' not in g:
            g.db = psycopg.connect(self.get_dsn())
        return g.db

    def disconnect(self, e=None):
        if 'db' in g:
            g.db.close()
        g.pop('db', None)