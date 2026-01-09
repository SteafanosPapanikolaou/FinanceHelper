from langchain_ollama.chat_models import ChatOllama

class LLMConnector(ChatOllama):

    @staticmethod
    def llm_connect(model = 'qwen3:4b', base_url = '') -> ChatOllama:
        """
        Interface for LLM Ollama API call

        :param model: str, from ollama list
        :param base_url: str, base url for Ollama
        :return:
        """

        llm = ChatOllama(model=model, base_url=base_url, temperature=0)

        return llm
