import logging
from typing import Optional, Union, Dict, Any

import neo4j
import psycopg2
import pymongo
import redis
from psycopg2.extras import RealDictCursor
from pymongo.errors import ConnectionFailure


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
                return None if len(result) == 0 else result
            except Exception as e:
                logging.error(f"Error while executing query {query} in {self.__class__.__name__}: {e}")
        else:
            logging.warning("PsqlDatabase failed to execute query on %s" % self.name)
            return None


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
        try:
            with self._driver.session() as session:
                result = session.run(query, parameters)
                return result
        except Exception as e:
            logging.error(f"Error while executing query %s in %s: %s" % (query, self.__class__.__name__, e))


class RedisConnection:
    def __init__(self, host: str, user: str, pswd: str):
        self.host = host
        self.user = user
        self.password = pswd
        self.conn: Optional[redis.Redis] = None

    def open(self):
        try:
            logging.info(f"Opening Redis connection for username {self.user}")
            self.connection = redis.Redis(host=self.host, username=self.user, password=self.password)
        except Exception as e:
            logging.error("Error while opening connection in %s: %s" % (self.__class__.__name__, e))

    def close(self):
        try:
            self.conn.close()
            print("Disconnected from Redis")
        except Exception as e:
            logging.error("Error while closing connection in %s: %s" % (self.__class__.__name__, e))

    def get(self, key: str) -> Union[str, bytes, None]:
        try:
            value = self.connection.get(key)
            logging.info(f"Retrieved value for {key} from Redis: {value}")
            return value
        except Exception as e:
            logging.error(f"Error getting value for {key} from Redis: {e}")
            return None

    def set(self, key: str, value: Union[str, bytes, int, float]):
        try:
            self.connection.set(key, value)
            logging.info(f"Set {key} to {value} in Redis")
        except Exception as e:
            logging.error(f"Error setting {key} in Redis: {e}")


class MongoDBConnection:
    def __init__(self, host:str, user:str, password:str, db_name: str):
        self.host = host
        self.user = user
        self.password = password
        self.db_name = db_name
        self.client: Optional[pymongo.MongoClient] = None
        self.db: Optional[pymongo.mongo_client.Database] = None


    def open(self):
        try:
            uri = f"mongodb://{self.user}:{self.password}@{self.host}:27017"
            logging.info(f"Opening MongoDB connection with URI: {uri}")
            self.client = pymongo.MongoClient(uri)
            self.db = self.client[self.db_name]
        except (Exception, ConnectionFailure) as e:
            logging.error("Error while opening connection in %s: %s" % (self.__class__.__name__, e))


    def close(self):
        try:
            logging.info(f"Closing MongoDB connection with DB {self.db_name}")
            self.client.close()
        except Exception as e:
            logging.error("Error while closing connection in %s: %s" % (self.__class__.__name__, e))


    def insert_document(self, collection_name: str, document: Dict[str, Any]) -> (str | None):
        try:
            collection = self.db[collection_name]
            result = collection.insert_one(document)
            print(f"Inserted document with ID: {result.inserted_id}")
            return str(result.inserted_id)
        except Exception as e:
            logging.error(f"Error inserting document into MongoDB: {e}")
            return None


    def get_document(self, collection_name: str, doc_id: str) -> Optional[Dict[str, Any]]:
        try:
            collection = self.db[collection_name]
            document = collection.find_one({"_id": doc_id})
            if document:
                print(f"Retrieved document with ID {doc_id} from MongoDB: {document}")
            return document
        except Exception as e:
            logging.error(f"Error getting document from MongoDB: {e}")
            return None
