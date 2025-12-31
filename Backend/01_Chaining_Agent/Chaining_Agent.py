from Backend.Connectors.Neo4j.neo4j_connector import Neo4jConnector
from Backend.Connectors.LLM_Connector import LLMConnector

class ChainingAgent:
    def __init__(self, credentials = '', model= 'qwen3:1.7b'):
        credentials = {"url": "http://localhost:7687",
                       "username": "neo4j",
                       "password": "12345678"}
        self.connector = Neo4jConnector(credentials=credentials)
        self.graph, self.msh = self.connector.neo4j_connector()
        self.llm = LLMConnector


    def create_kg(self, query):

        try:
            answer = self.llm.input(query=query)
            print(answer)
        except Exception as e:
            print(e)


if __name__ == '__main__':
    agent = ChainingAgent()
    query = 'hi'
    agent.create_kg(query=query)
