import unittest
from src.sweet_home import SweetConnections


class SweetConnectionsTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.sweet_connections = SweetConnections()
    

    def test_postgresql_insert_and_fetch(self):
        # Insert a user profile
        user_id = 123
        first_name = 'Test'
        last_name = 'User'
        self.sweet_connections.sql_connection.execute_query(
            "INSERT INTO user_profiles (user_id, first_name, last_name) VALUES (%s, %s, %s)",
            user_id, first_name, last_name)

        # Fetch the inserted user profile
        result = self.sweet_connections.sql_connection.execute_query_fetchone(
            "SELECT * FROM user_profiles WHERE user_id = %s", user_id)

        self.assertIsNotNone(result)
        self.assertEqual(result['first_name'], first_name)
        self.assertEqual(result['last_name'], last_name)

        # Clean up: delete the inserted user profile
        self.sweet_connections.sql_connection.execute_query(
            "DELETE FROM user_profiles WHERE user_id = %s", user_id)

        # Optionally, you can check if the deletion was successful
        result_after_deletion = self.sweet_connections.sql_connection.execute_query_fetchone(
            "SELECT * FROM user_profiles WHERE user_id = %s", user_id)
        self.assertIsNone(result_after_deletion)
        

    def test_neo4j_run_query(self):
        # Assuming you have a simple query to test the connection
        result = self.sweet_connections.neo4j_connection.run_query("CREATE (n: Node {test: 123}) RETURN n")
        self.assertIsNotNone(result)

        result = self.sweet_connections.neo4j_connection.run_query("MATCH (n) RETURN n LIMIT 1")
        self.assertIsNotNone(result)
        self.assertTrue(len(result) > 0)

        result = self.sweet_connections.neo4j_connection.run_query("MATCH (n: Node) WHERE n.test=123 DELETE n")
        self.assertIsNotNone(result)


    def test_mongodb_insert_and_find(self):
        # Insert a document
        collection_name = 'testCollection'
        document = {'name': 'Test', 'value': 123}
        inserted_id = self.sweet_connections.mongodb_connection.insert_document(collection_name, document)

        # Retrieve the document
        retrieved_document = self.sweet_connections.mongodb_connection.get_document(collection_name, inserted_id)
        self.assertIsNotNone(retrieved_document)
        self.assertEqual(retrieved_document['name'], document['name'])

        # Cleanup
        self.sweet_connections.mongodb_connection.delete_document(collection_name, inserted_id)


    def test_redis_set_and_get(self):
        # Set a value
        key = 'testKey'
        value = 'testValue'
        self.sweet_connections.redis_connection.set(key, value)

        # Get the value
        retrieved_value = self.sweet_connections.redis_connection.get(key)
        self.assertEqual(retrieved_value.decode('utf-8'), value)        


    @classmethod
    def tearDownClass(cls):
        cls.sweet_connections.sql_connection.close()

