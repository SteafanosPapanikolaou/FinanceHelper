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

@app.resource("data://config")
def example_data() -> str:
    """Provides sample resources"""
    return f'Useful Information'

@app.tool()
async def main(type_of_answer: str, ctx: Context) -> str:
    """Retrieve a type of answer based on the user request
    type_of_answer: user | reflect | knowledge_base
    Example:
    If query asks the user to answer: user
    If query asks the llm to answer: reflect
    If query asks the base to answer: knowledge_base
        """

    if type_of_answer == "user":
        answer = await ctx.elicit(
            message= 'Hello',
            response_type=str
        )
        if answer.answer == "accept":
            print(answer)
            return answer.data

    if type_of_answer == "reflect":
        answer = await ctx.sample("",
                                  system_prompt="How are you?",)
        print(answer.text)
        return answer.text

    if type_of_answer == "knowledge_base":
        data_uri = "data://config"
        await ctx.info(f"Knowledge base: {data_uri}")

        resource = await ctx.read_resource(data_uri)
        print(resource)
        data = resource[0].content if resource else ""
        print(data)
        return data


    return 'No answer'