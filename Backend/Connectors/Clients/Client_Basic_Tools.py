from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from Backend.Connectors.LLM_Connector import LLMConnector
import mcp
import asyncio

async def elicitation_callbak(context, params):
    q = input(f"Elicitation requested: {params}")
    return mcp.types.ElicitResult(action='accept', content={'value': q})

class MCPClient:
    def __init__(self):
        self.llm = LLMConnector.llm_connect(model='qwen3:4b')
        self.client = MultiServerMCPClient({
            "main_server": {
                "url": "http://localhost:8000/mcp",
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

        self.agent = create_agent(model=self.llm, tools=self.tools, system_prompt=self.prompt)

    async def generate_answer(self, query):
        # agent_answer = await self.agent.ainvoke({
        #     "messages": [{"role": "user", "content": query}],
        # })
        # return agent_answer['messages'][-1].content
        async for event in self.agent.astream({
            "messages": [{"role": "user", "content": query}],
        }):
            print(event)

        return event


async def main():
    client = MCPClient()
    await client.setup()
    query = (
        "Save to knowledge graph, my strategy. "
        "Buy a house at 40% market value and sell it when people are buying stocks."
    )
    a = await client.generate_answer(query)
    print(a)

if __name__ == '__main__':
    asyncio.run(main())
