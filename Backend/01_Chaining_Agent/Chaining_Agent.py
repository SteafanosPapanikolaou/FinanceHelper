from Backend.Connectors.Neo4j.neo4j_connector import Neo4jConnector
from Backend.Connectors.LLM_Connector import LLMConnector
from Backend.Connectors.prompt_lib.prompts_lib import AgentPromptLibrary
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, PromptTemplate, HumanMessagePromptTemplate

class ChainingAgent:
    def __init__(self, credentials = '', model= 'qwen3:4b', topic = 'Stock Market Strategy'):

        # Neo4j initialization
        if not credentials:
            credentials = {"url": "neo4j://127.0.0.1:7687",
                           "username": "neo4j",
                           "password": "12345678"}
        self.connector = Neo4jConnector(credentials=credentials)

        # Agentic Initialization
        self.llm = LLMConnector.llm_connect(model=model)
        self.agent_template = AgentPromptLibrary.chaining_agent_prompt()

        # Topic Initialization
        self.topic = topic

    def create_kg(self, query):
        """
        Create a knowledge graph on neo4j, based on the given query from user.
        :param query: str
        :return: KG on neo4j
        """
        try:
            agent_template = ChatPromptTemplate.from_messages(
                [
                    SystemMessagePromptTemplate(
                        prompt=PromptTemplate(template=self.agent_template, input_variables=["topic"]),
                    ),
                    HumanMessagePromptTemplate(
                        prompt=PromptTemplate(template=query, input_variables=[]),
                    )
                ]
            )
            agent_prompt = agent_template.invoke({"topic": self.topic})
            answer = self.llm.invoke(agent_prompt)

            with self.connector.driver.session() as session:
                session.run(answer)

        except Exception as e:
            print(e)


if __name__ == '__main__':
    agent = ChainingAgent()
    user_q = ('Buy if the current price is below open price. Sell when you spot 10% increase on the stock. Cut loss when'
              'you spot price of stock is below 25%.')
    agent.create_kg(query=user_q)
