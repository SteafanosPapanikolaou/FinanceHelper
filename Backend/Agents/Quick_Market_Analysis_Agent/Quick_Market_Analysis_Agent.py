from Backend.Connectors.LLM_Connector import LLMConnector
from Backend.Connectors.prompt_lib.prompts_lib import AgentPromptLibrary
from Backend.Connectors.Binance_Toolset.Strategy_Indication import produce_conclusion
from Backend.Connectors.Binance_Toolset.Binance_Tools import BinancePairCheck
from Backend.Connectors.News_Fetcher.Google_news_fetch import get_crypto_news
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnableLambda

def log_step(name):
    def _logger(x):
        print(f"\n🔹 {name} INPUT:\n", x)
        return x
    return RunnableLambda(_logger)

def market_report(crypto: str) -> str:
    news = get_crypto_news(crypto)
    result = "\n".join(item["title"] for item in news)
    return result

def onchain_report(crypto: str) -> str:
    match_maker = BinancePairCheck().check_binance_pair(crypto, 'tether')
    return produce_conclusion(match_maker)

class QuickMarketAnalysisAgent:
    def __init__(self,model='qwen3:1.7b'):

        self.llm = LLMConnector.llm_connect(model=model)

        prompts = AgentPromptLibrary.quick_market_recap_prompt()
        self.parallelizer_template = prompts["extract_crypto"]
        market_conclusion_template = prompts["market_conclusion"]
        on_chain_conclusion_template = prompts["on_chain"]

        extract_prompt = ChatPromptTemplate.from_template(
            self.parallelizer_template
        )

        extract_crypto_chain = extract_prompt | self.llm

        extract_text = RunnableLambda(lambda x: x.content)

        market_runnable = RunnableLambda(lambda x: market_report(x))
        onchain_runnable = RunnableLambda(lambda x: onchain_report(x))

        parallel_tools = RunnableParallel(
            market=market_runnable,
            onchain=onchain_runnable
        )

        market_conclusion_prompt = ChatPromptTemplate.from_template(market_conclusion_template)
        market_chain = market_conclusion_prompt | self.llm

        on_chain_conclusion_prompt = ChatPromptTemplate.from_template(on_chain_conclusion_template)
        on_chain_chain = on_chain_conclusion_prompt | self.llm

        self.full_pipeline = (
                {"query": RunnableLambda(lambda x: x)}
                | extract_crypto_chain
                | extract_text
                | parallel_tools
                | {
                    "market_conclusion": RunnableLambda(
                        lambda x: market_chain.invoke({"news": x["onchain"]})
                    ),
                    "onchain_conclusion": RunnableLambda(
                        lambda x: on_chain_chain.invoke({"report": x["market"]})
                    )
                }
                | RunnableLambda(lambda x: f"""
FINAL SYNTHESIS:
Market view: {x['market_conclusion'].content}
\nOn-chain view: {x['onchain_conclusion'].content}
                    """)
        )

    def quick_market_recap(self, user_input):
        result = self.full_pipeline.invoke(
            q
        )

        return result

if __name__ == '__main__':
    q = 'What is the trend on the Ethereum?'
    agent = QuickMarketAnalysisAgent()
    agent.quick_market_recap(q)
