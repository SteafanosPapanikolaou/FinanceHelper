from fastmcp import FastMCP, Context
from fastmcp.client.sampling import SamplingMessage, SamplingParams, RequestContext
from langchain_core.prompts import PromptTemplate
from Backend.Connectors.LLM_Connector import (LLMConnector)

from Backend.Agents.Chaining_Agent.Chaining_Agent import ChainingAgent


async def basic_sampling_handler(messages: list[SamplingMessage], params: SamplingParams, context: RequestContext):
    system_prompt = params.systemPrompt or "You are a helpful assistant."
    llm = LLMConnector(model='qwen3:4b')
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

    # Handle user_summary
    if not user_summary:
        answer = await ctx.elicit(
            message='Please describe the strategy you want to save at the knowledge graph.',
            response_type=str
        )
        if answer.answer == "accept":
            user_summary = answer.data

        if not topic:
            answer = await ctx.sample("",
                                      system_prompt=f"Read the Context. "
                                                    f"If explicitly stated, describe the topic, else return ''."
                                                    f"Context: {user_summary}", )
            topic = answer.text

    # Handle topic
    if not topic:

        answer = await ctx.elicit(
            message='I was not able to pinpoint the topic, of your strategy please describe it.',
            response_type=str
        )
        if answer.answer == "accept":
            topic = answer.data

    # Use of agent.
    sub_agent_chainer = ChainingAgent(topic=topic)
    sub_agent_chainer.create_kg(query=user_summary)

    return 'Successfully created the Knowledge Graph'

@app.tool()
async def read_strategy(ctx: Context) -> str:
    """Read the saved strategy from the knowledge graph. """

    return 'Successfully read the strategy.'


@app.tool()
async def take_action(ctx: Context) -> str:
    """Take action set by user. """

    return 'Successfully action happened.'

if __name__ == '__main__':
    app.run(transport="http", port=8000)
