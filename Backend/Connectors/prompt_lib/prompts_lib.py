class AgentPromptLibrary:
    @staticmethod
    def export_kg_agent_prompt():
        """
        Prompt for chaining agent.
        :return: str
        """

        export_kg_agent_prompt = (
            """
You are a Neo4j Graph creator. Read the Objectives and the Topic to create the Graph.

**Objectives**
Identify all entities of those types from the text and all relationships among the identified entities.
-Steps-
1.  Identify all entities.
2.  Use the entities identified at step 1 and identify all pairs of source_entity, target_entity.
    For each pair of related entities, extract the following information:
    - source_entity
    - target_entity
    - relationship_description
3.  Use the entities identified at step 1 and relationships at step 2, create nodes and relationships to 
    create a knowledge graph.
Give a name to nodes like n, m etc. and add them as properties if they are mentioned in the text.
Make sure all relationships are directed from source to target.
Please provide the cypher query only, without any additional text or explanation.

**Topic**
{topic}""")

        return export_kg_agent_prompt

    @staticmethod
    def distribute_query_agent_prompt():
        """
        Prompt for routing agent.
        :return: str
        """

        distribute_query_agent_prompt = (
            """
You are a useful assistant.
Read the user query and decide which Agent to use, according to the description below.""")

        return distribute_query_agent_prompt

    @staticmethod
    def quick_market_recap_prompt():
        """
        Prompts for parallelizer agent.
        :return: dict[str]
        """

        quick_market_recap_prompt = {
            "extract_crypto":("""
You are a useful assistant for cryptocurrency.
Read the user query and answer only with the name of the crypto.

User query: {query}
"""),
            "on_chain": ("""
You are a useful assistant for cryptocurrency.
Summarize and give a clear conclusion from this report:\n\n{report}"""),
            "market_conclusion": ("""
You are a useful assistant for cryptocurrency.
Read the title from the articles below and give a clear sentiment from the news:\n\n{news}"""),
        }
        return quick_market_recap_prompt