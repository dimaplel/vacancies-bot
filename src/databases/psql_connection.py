import logging

import psycopg2
from psycopg2.extras import RealDictCursor


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
            self.cur = self.conn.cursor(cursor_factory=RealDictCursor) # Use dict-only access to query result
        except (Exception, psycopg2.DatabaseError) as e:
            logging.error("Error while opening connection in %s: %s" % (self.__class__.__name__, e))
        
        
    def close(self):
        logging.info(f"Closing PsqlDatabase connection with {self.name}")
        try:
            self.cur.close()
            self.conn.close()
        except Exception as e:
            logging.error("Error while closing connection in %s: %s" % (self.__class__.__name__, e))
            

    def execute_query(self, query: str, *args):
        if self.cur is not None:
            try:
                self.cur.execute(query, args)

                # Check if there are results to fetch. If desc is none - there is no results
                if self.cur.description is None:
                    return None

                result = self.cur.fetchall()
                return None if result.count() == 0 else result
            except Exception as e:
                logging.error(f"Error while executing query {query} in {self.__class__.__name__}: {e}")
        else:
            logging.warning("PsqlDatabase failed to execute query on %s" % self.name)
            return None