from neo4j import GraphDatabase

class Neo4jConnector:
    def __init__(self, credentials):
        self.driver = GraphDatabase.driver(credentials['url'], auth=(credentials['username'], credentials['password']))

    def neo4j_connect_test(self):
        with self.driver as driver:
            driver.verify_connectivity()
            return driver, f'Connected to Neo4j'

    def neo4j_disconnect(self):
        with self.driver as driver:
            driver.close()

    def neo4j_delete_nodes_and_relationships(self):
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
