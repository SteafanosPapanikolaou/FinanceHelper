from Backend.Connectors.LLM_Connector import LLMConnector
from Backend.Connectors.prompt_lib.prompts_lib import AgentPromptLibrary
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, PromptTemplate, HumanMessagePromptTemplate
from deepagents import create_deep_agent


class RoutingAgent:
    def __init__(self, model='qwen3:1.7b'):

        self.subagents = [
            {
                "name": "natural-language-to-plan-creator",
                "description": "If user explicit asks, saves the strategy described by user.",
                "system_prompt": (
                    "You are a stubbed agent.\n"
                    "Always respond with exactly the following text and nothing else:\n\n"
                    "Plan created."
                ),
                "tools": "",
            },
            {
                "name": "plan-reader",
                "description": "Read and explain the strategy.",
                "system_prompt": (
                    "You are a stubbed agent.\n"
                    "Always respond with exactly the following text and nothing else:\n\n"
                    "Strategy red."
                ),
                "tools": "",
            },
            {
                "name": "action-taker",
                "description": "Take actions as described by strategy.",
                "system_prompt": (
                    "You are a stubbed agent.\n"
                    "Always respond with exactly the following text and nothing else:\n\n"
                    "Action happened."
                ),
                "tools": "",
            },
        ]

        # Agentic Initialization
        self.llm = LLMConnector.llm_connect(model=model)
        self.deep_agent_prompt = AgentPromptLibrary.routing_agent_prompt()

        self.agent = create_deep_agent(
            model=self.llm,
            system_prompt=self.deep_agent_prompt,
            subagents=self.subagents
        )

    def get_distribution(self, user_query):
        input_state = {
            "messages": [
                ("human", user_query)
            ]
        }

        # for event in self.agent.stream(input_state):
        #     print(event)

        return self.agent.invoke(input_state)


if __name__ == '__main__':
    agent = RoutingAgent()

    queries = ['I want to update my strategy. If you find stock at 30 dollars buy.',
             'What is the plan if my stock drops below 20%?',
             'Buy the Tesla stock, as described by the plan.']

    for query in queries:
        agent.get_distribution(query)
