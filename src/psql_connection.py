import logging

import psycopg2

class PsqlConnection:

    def __init__(self, db_name: str, db_host: str, db_user: str, db_pswd: str):
        self.name = db_name
        self.host = db_host
        self.user = db_user
        self._conn = psycopg2.connect(
            host=self.host, 
            dbname=self.name, 
            user=self.user, 
            password=db_pswd)
        self.cur = self._conn.cursor()
        logging.info(f"Opening Psql connection with {self.name}")
        
        
    def __enter__(self):
        return self
        
    
    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()
        
        
    def close(self):
        logging.info(f"Closing PsqlDatabase connection with {self.name}")
        try:
            self.cur.close()
            self._conn.close()
        except TypeError as t:  
            logging.critical(t)
            

    def execute_query(self, query: str, *args) -> None:
        if self.cur is not None:
            self.cur.execute(query, args)
        else:
            logging.info("PsqlDatabase failed to execute query on {}", self.name)