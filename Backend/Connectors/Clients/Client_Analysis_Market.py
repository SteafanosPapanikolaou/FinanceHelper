from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from Backend.Connectors.LLM_Connector import LLMConnector
import asyncio


class MCPClientMarketAnalysis:
    def __init__(self):
        self.llm = LLMConnector.llm_connect(model='qwen3:1.7b')
        self.client = MultiServerMCPClient({
            "market_analysis_server": {
                "url": "http://localhost:8001/mcp",
                "transport": "streamable_http",
            }
        })
        self.tools = None
        self.prompt = ('Create reports that the user might need. Create the reports so it is easy to read.'
                       'Respond in plain text only.')
        self.agent = None

        self.RAW_TOOLS = {
            "article_report_creation",
        }

    async def setup(self):
        self.tools = await self.client.get_tools()

        self.agent = create_agent(model=self.llm, tools=self.tools, system_prompt=self.prompt)


    async def safe_invoke(self, agent, input_data):
        result = await agent.ainvoke(input_data)

        # Check if tools were used
        steps = result.get("intermediate_steps", [])

        if not steps:
            return result["output"]

        # Last tool used
        last_tool, last_tool_output = steps[-1]

        if last_tool.tool in self.RAW_TOOLS:
            # 🔥 RETURN RAW TOOL OUTPUT
            return last_tool_output

        return result["output"]

    async def generate_answer(self, query):
        agent_answer = await self.agent.ainvoke({
            "messages": [{"role": "user", "content": query}],
        })
        return agent_answer['messages'][-1].content
        # async for event in self.agent.astream({
        #     "messages": [{"role": "user", "content": query}],
        # }):
        #     print(event)
        #
        # return event


async def main():
    client = MCPClientMarketAnalysis()
    await client.setup()

    queries = [
        # 'Give me a market report on Etherium Coin.',
        # 'Give me a on chain report for the solana Coin',
        'Give me a report from the articles for the binance Coin',
    ]

    for query in queries:
        a = await client.generate_answer(query)
        print(a)

if __name__ == '__main__':
    asyncio.run(main())
