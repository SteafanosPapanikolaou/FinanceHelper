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

        self.RAW_TOOLS = None
        self.RAW_TITLES = {}

    async def setup(self):
        self.tools = await self.client.get_tools()

        self.RAW_TOOLS = set()

        for tool in self.tools:
            if getattr(tool, "metadata", {}).get("_meta").get("raw_output") is True:
                self.RAW_TOOLS.add(tool.name)
                self.RAW_TITLES.update({tool.name: tool.metadata.get("_meta").get("report_title")})

        self.agent = create_agent(model=self.llm, tools=self.tools, system_prompt=self.prompt)

    async def generate_answer(self, query):
        raw_outputs = []

        async for event in self.agent.astream_events({
            "messages": [{"role": "user", "content": query}],
        },
                version="v2"):

            if event["event"] == "on_tool_end":
                tool_name = event["name"]

                if tool_name in self.RAW_TOOLS:
                    raw_outputs.append(self.RAW_TITLES[tool_name] +'\n\n' +(event["data"]["output"].content[0]['text']))

            if event["event"] == "on_chat_model_start" and raw_outputs:
                return "\n-----------------\n".join(raw_outputs)


async def main():
    client = MCPClientMarketAnalysis()
    await client.setup()

    queries = [
        'Give me a market report on Etherium Coin, both from on chain and articles.',
        'Give me a on chain report for the solana Coin',
        'Give me a report from the articles for the binance Coin',
    ]

    for query in queries:
        a = await client.generate_answer(query)
        print(a)

if __name__ == '__main__':
    asyncio.run(main())
