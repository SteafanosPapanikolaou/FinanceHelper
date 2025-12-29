from langchain_ollama.llms import OllamaLLM

class LLMConnector(OllamaLLM):

    @staticmethod
    def llm_connect(model = 'qwen3:4b', base_url = '') -> OllamaLLM:
        """
        Interface for LLM Ollama API call

        :param model: str, from ollama list
        :param base_url: str, base url for Ollama
        :return:
        """

        llm = OllamaLLM(model=model, base_url=base_url, temperature=0)

        return llm
