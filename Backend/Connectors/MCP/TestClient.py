from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from Backend.Connectors.LLM_Connector import LLMConnector
import mcp

async def elicitation_callbak(context, params):
    q = input(f"Elicitation requested: {params}")
    return mcp.types.ElicitResult(action='accept', content={'value': q})

class MCPClient:
    def __init__(self):
        self.llm = LLMConnector(model='qwen3:1.7b')
        self.client = MultiServerMCPClient({
            "main_server": {
                "url": "http://localhost:8001/mcp",
                "transport": "streamable_http",
                "session_kwargs": {
                    "elicitation_callback": elicitation_callbak,
                }
            }
        })
        self.tools = None
        self.prompt = 'You are a helpful assistant.'
        self.agent = None

    async def setup(self):
        self.tools = await self.client.get_tools()

        self.agent = create_react_agent(self.llm, self.tools, prompt=self.prompt)

    async def generate_answer(self, query):
        agent_answer = await self.agent.ainvoke({
            "messages": [{"role": "user", "content": query}],
        })

        return agent_answer['messages'][-1].content
