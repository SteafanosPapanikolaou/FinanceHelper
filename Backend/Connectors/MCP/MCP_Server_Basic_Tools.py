from fastmcp import FastMCP, Context
from fastmcp.client.sampling import SamplingMessage, SamplingParams, RequestContext
from langchain_core.prompts import PromptTemplate
from Backend.Connectors.LLM_Connector import (LLMConnector)

async def basic_sampling_handler(messages: list[SamplingMessage], params: SamplingParams, context: RequestContext):
    system_prompt = params.systemPrompt or "You are a helpful assistant."
    llm = LLMConnector(model = 'qwen3:1.7b')
    qa_prompt = PromptTemplate(template=system_prompt)

    qa_chain = qa_prompt | llm

    result = qa_chain.invoke({"message": system_prompt})

    return result

app = FastMCP("main_server", sampling_handler=basic_sampling_handler)


@app.tool()
async def strategy_to_knowledge_graph(user_summary: str, topic: str, ctx: Context) -> str:
    """Saves the user strategy to knowledge graph.
    user_summary: Summarize the user strategy.
    topic: If explicitly stated describe the topic | '' """

    print(user_summary)
    print(topic)

    return 'Success'

if __name__ == '__main__':
    app.run(transport="http", port=8000)
