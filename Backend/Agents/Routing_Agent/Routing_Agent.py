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
        self.agent_template = AgentPromptLibrary.chaining_agent_prompt()

        self.agent = create_deep_agent(
            model="claude-sonnet-4-5-20250929",
            system_prompt="You coordinate data analysis and reporting. Use subagents for specialized tasks.",
            subagents=self.subagents
        )


if __name__ == '__main__':
    agent = RoutingAgent()
