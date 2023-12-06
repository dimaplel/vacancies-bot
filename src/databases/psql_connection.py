import logging

import psycopg2


class PsqlConnection:
    def __init__(self, db_host: str, db_name: str, db_user: str, db_pswd: str):
        self.name = db_name
        self.host = db_host
        self.user = db_user
        self.password = db_pswd
        self.conn = None
        self.cur = None
        

    def open(self):
        try:
            logging.info(f"Opening PsqlDatabase connection with {self.name}")
            self.conn = psycopg2.connect(host=self.host, dbname=self.name, user=self.user, password=self.password)
            self.conn.autocommit = True
            self.cur = self.conn.cursor()
        except (Exception, psycopg2.DatabaseError) as e:
            logging.error("Error while opening connection in %s: %s" % (self.__class__.__name__, e))
        
        
    def close(self):
        logging.info(f"Closing PsqlDatabase connection with {self.name}")
        try:
            self.cur.close()
            self.conn.close()
        except Exception as e:
            logging.error("Error while closing connection in %s: %s" % (self.__class__.__name__, e))
            

    def execute_query(self, query: str, *args) -> None:
        if self.cur is not None:
            self.cur.execute(query, args)
        else:
            logging.info("PsqlDatabase failed to execute query on {}", self.name)