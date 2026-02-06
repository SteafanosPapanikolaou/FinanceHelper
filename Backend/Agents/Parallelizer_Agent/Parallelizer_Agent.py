from Backend.Connectors.LLM_Connector import LLMConnector
from Backend.Connectors.prompt_lib.prompts_lib import AgentPromptLibrary
from Backend.Connectors.Binance_Toolset.Strategy_Indication import produce_conclusion
from Backend.Connectors.News_Fetcher.Google_news_fetch import get_crypto_news
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel
from langchain_core.runnables import RunnableLambda

def log_step(name):
    def _logger(x):
        print(f"\n🔹 {name} INPUT:\n", x)
        return x
    return RunnableLambda(_logger)

def market_report(crypto: str) -> str:
    return get_crypto_news(crypto)

def onchain_report(crypto: str) -> str:
    return produce_conclusion(crypto)

class ParallelizerAgent:
    def __init__(self,q, model='qwen3:1.7b'):

        # Agentic Initialization
        self.llm = LLMConnector.llm_connect(model=model)

        prompts = AgentPromptLibrary.parallelizer_agent_prompt()
        self.parallelizer_template = prompts["parallelizer"]
        self.conclusion_agent_template = prompts["conclusion_agent"]

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

        full_pipeline = (
                {"query": RunnableLambda(lambda x: x)}
                | log_step("USER QUERY")
                | extract_crypto_chain
                | log_step("EXTRACTED CRYPTO")
                | extract_text
                | log_step("EXTRACTED TEXT")
                | parallel_tools
                | log_step("TOOL Answers"))

        result = full_pipeline.invoke(
            q
        )

if __name__ == '__main__':
    q = 'What is the trend on the Ethereum?'
    agent = ParallelizerAgent(q= q)

    # user_q = ('Buy if the current price is below open price. Sell when you spot 10% increase on the stock. Cut loss when'
    #           'you spot price of stock is below 25%.')
    # agent.create_kg(query=user_q)