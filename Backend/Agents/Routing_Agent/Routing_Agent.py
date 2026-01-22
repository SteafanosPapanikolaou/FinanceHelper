import time
from Backend.Connectors.LLM_Connector import LLMConnector
from Backend.Connectors.prompt_lib.prompts_lib import AgentPromptLibrary
from langchain_core.prompts import (ChatPromptTemplate, SystemMessagePromptTemplate, PromptTemplate,
                                    HumanMessagePromptTemplate)


class RoutingAgent:
    def __init__(self, model='qwen3:4b'):

        self.dict = {
            "update-strategy" : {"explanation" : "Use to update the strategy.", "tool" : "Placeholder: Strategy updated"},
            "read-strategy" : {"explanation" : "Use to read the strategy.", "tool" : "Placeholder: Strategy read"},
            "action-taker" : {"explanation" : "Use to take an action.", "tool" : "Placeholder: Action happened"},
        }

        # Agentic Initialization
        self.llm = LLMConnector.llm_connect(model=model)
        self.agent_template = self._create_routing_prompt()

    def _create_routing_prompt(self):
        rout_prompt = AgentPromptLibrary.routing_agent_prompt()
        k = 1
        for key, value in self.dict.items():
            rout_prompt =rout_prompt + f'\n{str(k)}. {value["explanation"]} Answer "{key}"'
            k = k + 1
        return rout_prompt

    def _take_action(self, tool_caller):
        if tool_caller in self.dict:
            print(self.dict[tool_caller]["tool"])


    def get_distribution(self, user_query):
        agent_template = ChatPromptTemplate.from_messages(
            [
                SystemMessagePromptTemplate(
                    prompt=PromptTemplate(template=self.agent_template, input_variables=[]),
                ),
                HumanMessagePromptTemplate(
                    prompt=PromptTemplate(template=user_query, input_variables=[]),
                )
            ]
        )
        agent_prompt = agent_template.invoke({})
        answer = self.llm.invoke(agent_prompt)
        self._take_action(answer.content)


if __name__ == '__main__':
    agent = RoutingAgent()

    queries = [
        'I want to update my strategy. If you find stock at 30 dollars buy.',
        'What is the plan if my stock drops below 20%?',
        'Buy the Tesla stock.'
    ]

    for query in queries:
        agent.get_distribution(query)
