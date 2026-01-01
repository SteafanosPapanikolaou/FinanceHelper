import asyncio
from fastmcp import Client

client = Client("http://localhost:8000/mcp")

async def call_tool(name):
    async with client:
        result = await client.call_tool("main_server",
                                {
                                "main":{"type_of_answer": name},
                                        })
        print(result)

asyncio.run(call_tool("user"))
