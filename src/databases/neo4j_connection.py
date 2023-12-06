import logging
from typing import Optional

import neo4j

class Neo4jConnection:
    def __init__(self, host: str, user: str, password: str, port: int = 7687):
        self._driver: Optional[neo4j.Driver] = None
        self.host = host
        self.user = user
        self.password = password
        self.port = port


    def open(self):
        try:
            uri = f"bolt://{self.host}:{self.port}"
            logging.info(f"Connecting to neo4j database with uri {uri}")
            self._driver = neo4j.GraphDatabase.driver(uri=uri, auth=(self.user, self.password))
        except Exception as e:
            logging.error("Error while opening connection in %s: %s" % (self.__class__.__name__, e))


    def close(self):
        try:
            logging.info("Closing neo4j connection for ")
            self._driver.close()
        except Exception as e:
            logging.error("Error while closing connection in %s: %s" % (self.__class__.__name__, e))


    def run_query(self, query, parameters=None):
        with self._driver.session() as session:
            result = session.run(query, parameters)
            return result