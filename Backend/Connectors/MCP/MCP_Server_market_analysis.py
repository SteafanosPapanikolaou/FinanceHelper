from fastmcp import FastMCP, Context
from fastmcp.client.sampling import SamplingMessage, SamplingParams, RequestContext
from langchain_core.prompts import PromptTemplate
from Backend.Connectors.LLM_Connector import (LLMConnector)
from Backend.Connectors.Binance_Toolset.Strategy_Indication import produce_conclusion
from Backend.Connectors.Binance_Toolset.Binance_Tools import BinancePairCheck
from Backend.Connectors.News_Fetcher.Google_news_fetch import get_crypto_news


def market_report(crypto: str,max_items:int=5) -> str:
    news = get_crypto_news(crypto, max_items=max_items)
    result = "\n".join(item["title"] for item in news)
    return result

def onchain_report(crypto: str) -> str:
    match_maker = BinancePairCheck().check_binance_pair(crypto, 'tether')
    return produce_conclusion(match_maker)


async def basic_sampling_handler(messages: list[SamplingMessage], params: SamplingParams, context: RequestContext):
    system_prompt = params.systemPrompt or "You are a helpful assistant."
    llm = LLMConnector(model='qwen3:1.7b')
    qa_prompt = PromptTemplate(template=system_prompt, input_variables= [])

    qa_chain = qa_prompt | llm

    result = qa_chain.invoke({"message": system_prompt})

    return result.content

app = FastMCP("market_analysis_server", sampling_handler=basic_sampling_handler)


@app.tool(
    meta = {
        "raw_output": True,
        "report_title": "Trending Articles",
    }
)
async def article_report_creation(crypto_name: str, ctx: Context, number_of_articles: int = 5) -> str:
    """Creates a report, based on most trending articles.
    crypto_name: Cryptocurrency of interest.
    number_of_articles: Number of articles to report."""

    report= market_report(crypto_name)

    answer = await ctx.sample("",
                              system_prompt=f"Read the Article titles."
                                            f"Crete a brief report, focusing mainly on the general sentiment."
                                            f"Article titles:\n{report}", )

    print(answer.text)
    report = answer.text

    return report

@app.tool(
    meta = {
            "raw_output": True,
            "report_title": "On-Chain Analysis",
        }
)
async def on_chain_report(crypto_name: str, ctx: Context) -> str:
    """Creates a report, from on chain analysis.
    crypto_name: Cryptocurrency of interest."""

    report = onchain_report(crypto_name)

    return report


if __name__ == '__main__':
    app.run(transport="http", port=8001)
