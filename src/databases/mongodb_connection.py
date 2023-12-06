import logging
import pymongo
from pymongo.errors import ConnectionFailure
from typing import Optional, Union, Any, Dict, Collection

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


    def insert_document(self, collection_name: str, document: Dict[str, Any]) -> Union[str, None]:
        try:
            collection = self.db[collection_name]
            result = collection.insert_one(document)
            print(f"Inserted document with ID: {result.inserted_id}")
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error inserting document into MongoDB: {e}")
            return None


    def get_document(self, collection_name: str, doc_id: str) -> Optional[Dict[str, Any]]:
        try:
            collection = self.db[collection_name]
            document = collection.find_one({"_id": doc_id})
            if document:
                print(f"Retrieved document with ID {doc_id} from MongoDB: {document}")
            return document
        except Exception as e:
            print(f"Error getting document from MongoDB: {e}")
            return None