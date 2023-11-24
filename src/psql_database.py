import logging

import psycopg2

class PsqlDatabase:

    def __init__(self, db_name: str):
        self.name = db_name
        

    def open(self, db_user: str, db_pswd: str):
        logging.info("Opening PsqlDatabase connection with {}", self.name)
        self.user = db_user
        self.conn = psycopg2.connect(database = self.name, user = self.user, password = db_pswd)
        self.cur = self.conn.cursor()
        
        
    def close(self):
        logging.info("Closing PsqlDatabase connection with {}", self.name)
        try:
            self.cur.close()
            self.conn.close()
        except TypeError as t:  
            logging.error(t)
            

    def execute_query(self, query: str, *args) -> None:
        if self.cur is not None:
            self.cur.execute(query, args)
        else:
            logging.info("PsqlDatabase failed to execute query on {}", self.name)