class AgentPromptLibrary:
    @staticmethod
    def chaining_agent_prompt():
        """
        Prompt for chaining agent.
        :return: str
        """

        chaining_agent_prompt = (
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

        return chaining_agent_prompt