from pydantic import BaseModel, Field
from langchain.agents import create_agent
from Backend.Connectors.LLM_Connector import LLMConnector
from Backend.Connectors.prompt_lib.prompts_lib import AgentPromptLibrary
from typing import Any, Literal, TypedDict
from datetime import datetime
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END


# State
class State(TypedDict):
    input: str
    subject: str
    value: str
    completeness_iteration: int
    correctness_confidence: float
    correctness_question: str
    correctness_value: str
    correctness_iteration: int
    question_to_user: str


class FieldState(BaseModel):
    value: Any = None
    completeness_question: str
    correctness_confidence: float = 0.0
    source: Literal["user", "inferred", "corrected"] = None
    timestamp: datetime = None
    iteration: int = 0


class TradingPlan(BaseModel):
    entry_condition: str | None = Field(default=None, description="Entry condition.")
    entry_point: str | None = Field(default=None, description="Entry point.")
    stop_loss: str | None = Field(default=None, description="Stop loss.")
    take_profit: str | None = Field(default=None, description="Take profit.")
    position_size: str | None = Field(default=None, description="Position size.")


# state = {
#     "entry_condition": FieldState(completeness_question="Buy when news are positive?"),
#     "entry_point": FieldState(completeness_question="Buy in at the current price?"),
#     "stop_loss": FieldState(completeness_question="10% of the entry point?"),
#     "take_profit": FieldState(completeness_question="15% of the entry point?"),
#     "position_size": FieldState(completeness_question="2% of portofolio?"),
# }
#
# model = 'qwen3:4b'
# llm = LLMConnector.llm_connect(model=model)
# agent = create_agent(
#     model=llm,
#     response_format=TradingPlan,
#     system_prompt="""
# You are a financial information extraction system.
#
# Extract ONLY explicitly stated values.
#
# If the value is missing, output null.
#
# Never infer or guess.
#
# Missing means null.
# """
# )
#
# user_input = ("When we see bad news for BTC and the price is lower than 58k. "
#              "Use less than 2% of the portofolio."
#              "Sell when the price of BTC is 10% on the upside or more, but remember to sell the"
#              "position out if price falls more than 15%.")
#
# result = agent.invoke({
#     "messages": [{"role": "user", "content": user_input}],
# })
#
# plan = result["structured_response"].model_dump()
#
# for key, value in plan.items():
#     if key in state:
#         state[key].value = value
#
# for i in state.keys():
#     print(i,":", state[i].value)
#
# state["entry_condition"].value = None
# state["entry_condition"].value = ("entry_condition: "
#                                   "- BTC and the price is lower than 58k "
#                                   "exit_conditions: "
#                                   "- Sell when the price of BTC is 10% on the upside or more "
#                                   "- Sell the position out if price falls more than 15%.")
# state["entry_point"].value = '58000'
# state["stop_loss"].value = '15%'
# state["take_profit"].value = '10%'
# state["position_size"].value = None
# state["position_size"].value = "Position Size: Less than 2% of portfolio."
# model = 'granite4:3b'
# llm = LLMConnector.llm_connect(model=model)
# for subject in state.keys():

#     if state[subject].value is None:
#         print('Working on completness')
#         print(subject, state[subject].value)
#
#         completeness_prompt = f"Extract information only about {subject}."
#         question_prompt = completeness_prompt
#
#         reflection_prompt = f"""
# User input:
# {user_input}
#
# {question_prompt}
# """
#
#         agent = create_agent(
#             model=llm,
#             system_prompt="""
# You are a financial information extraction system.
#
# Extract ONLY relevant information.
# No additional text needed.
#
# If the value is missing, output null.
#
# Never infer or guess.
#
# Missing means null.
# """
#         )
#
#         result = agent.invoke({
#             "messages": [{"role": "user", "content": reflection_prompt}],
#         })
#
#         print(result['messages'][-1].content)
#         # print(result["structured_response"])
#         print()
#
#         state[subject].value = result['messages'][-1].content

#     if state[subject].value is not None:
#         print('Working on correctness')
#         print(subject, state[subject].value)
#
#
class CheckCorrectnessPlan(BaseModel):
    fixed_value: str | None = Field(default=None, description="Fixed value.")
    clarification_question: str | None = Field(default=None, description="Clarification Question")
    correctness_confidence: float = Field(default=0.0, description="Evaluation confidence")
#
#         correctness_prompt = f"""
# Subject in question:
# {subject}
#
# User input:
# {user_input}
#
# Extracted output:
# {state[subject].value}
# """
#
#         agent = create_agent(
#             model=llm,
#             response_format=CheckCorrectnessPlan,
#             system_prompt="""
# You are going to evaluate the Extracted output from the User input for the Subject in question.
#
# Output an Evaluation confidence from 0 to 100.
#
# If the Output less than 80.
# Create a Clarification Question for the user.
#
# If the Output more than 80.
# Return null
# """
#         )
#
#         result = agent.invoke({
#             "messages": [{"role": "user", "content": correctness_prompt}],
#         })
#
#         # print(result['messages'][-1].content)
#         # print(result["structured_response"])
#         # print()
#
#         state[subject].correctness_confidence = result["structured_response"].correctness_confidence
#         state[subject].completeness_question = result["structured_response"].clarification_question
#
# for i in state.keys():
#     print(state[i])
#     print()

class TradePlanEvaluatorAgent:
    def __init__(self, model='qwen3:1.7b'):

        self.llm_extractor = LLMConnector.llm_connect(model='qwen3:0.8b')
        self.llm_check_lvl1 = LLMConnector.llm_connect(model=model)
        self.llm_check_lvl2 = LLMConnector.llm_connect(model='qwen3:4b')
        self.memory = MemorySaver()

        self.state = {
            "entry_condition": FieldState(completeness_question="Buy when news are positive?"),
            "entry_point": FieldState(completeness_question="Buy in at the current price?"),
            "stop_loss": FieldState(completeness_question="10% of the entry point?"),
            "take_profit": FieldState(completeness_question="15% of the entry point?"),
            "position_size": FieldState(completeness_question="2% of portofolio?"),
        }

        prompts = AgentPromptLibrary.trade_plan_evaluator_prompt()
        self.extract_from_conversation_template = prompts["extract_from_conversation"]
        self.extract_one_subject_template = prompts["extract_one_subject"]
        self.ask_completeness_question_template = prompts["ask_completeness_question"]
        self.correctness_evaluation_template = prompts["correctness_evaluation"]

        self.extraction_agent = create_agent(
            model=self.llm_extractor,
            response_format=TradingPlan,
            system_prompt=self.extract_from_conversation_template
        )

        self.llm_check_lvl1_agent = create_agent(
            model=self.llm_check_lvl1,
            system_prompt=self.extract_one_subject_template
        )

        self.ask_completeness_question_agent = create_agent(
            model=self.llm_check_lvl1,
            system_prompt=self.ask_completeness_question_template,
            checkpointer=self.memory
        )

        self.correctness_evaluator_agent = create_agent(
                        model=self.llm_check_lvl2,
                        response_format=CheckCorrectnessPlan,
                        system_prompt=self.correctness_evaluation_template
                    )

        self._langgraph_agent()

        # result = self.extraction_agent.invoke({
        #     "messages": [{"role": "user", "content": user_input}],
        # })
        #
        # plan = result["structured_response"].model_dump()
        #
        # for key, value in plan.items():
        #     if key in self.state:
        #         self.state[key].value = value

    def _langgraph_agent(self):
        def route_completeness(state: State) -> str:
            if state["value"] is None and state["completeness_iteration"]<3:
                return "ExtractSingleInformation"
            return "Pass"

        def completeness_inner_route(state: State):
            if state["value"]:
                return "Pass"

            if state["completeness_iteration"]<2:
                return "AskCompletenessQuestion"
            return "SuggestQuestion"

        def extract_single_information(state: State):
            reflection_prompt = f"""
            User input:
            {state["input"]}

            Extract information only about: {state["subject"]}
            """
            result = self.llm_check_lvl1_agent.invoke(
                {"messages": [{"role": "user", "content": reflection_prompt}]},
            )
            return {
                "value": result.content,
                "completeness_iteration": state["completeness_iteration"]+1
                    }

        def ask_completeness_question(state: State):
            ask_completeness_question_prompt = f"""
            Subject: {state["subject"]}
            """
            result = self.ask_completeness_question_agent.invoke(
                {"messages": [{"role": "user", "content": ask_completeness_question_prompt}]},)
            return {"question_to_user": result.content}

        def suggest_question(state: State):
            return {"question_to_user": self.state[state["subject"]].completeness_question}

        def correctness_evaluator(state: State):
            correctness_prompt = f"""
            Subject in question:
            {state["subject"]}

            User input:
            {state["input"]}

            Extracted question_to_user:
            {state["value"]}
            """
            result = self.correctness_evaluator_agent.invoke(
                {"messages": [{"role": "user", "content": correctness_prompt}]}, )
            return {
                "correctness_confidence": result["structured_response"].correctness_confidence,
                "correctness_question": result["structured_response"].clarification_question,
                "correctness_value": result["structured_response"].fixed_value,
                "correctness_iteration": state["correctness_iteration"]+1,
            }

        def route_correctness(state: State) -> str:
            if state["correctness_iteration"]<3:
                if state["correctness_confidence"] <80.0 and state["correctness_value"] is not None:
                    return "FixValue"
                if state["correctness_confidence"] <60.0:
                    return "AskCorrectnessQuestion"
            return "Pass"

        def fix_value(state: State):
            return {"value": state["correctness_value"]}

        def ask_correctness_question(state: State):
            return {"question_to_user": state["correctness_question"]}

        # Build workflow
        router_builder = StateGraph(State)

        # Add nodes
        router_builder.add_node("route_completeness", route_completeness)
        router_builder.add_node("ExtractSingleInformation", extract_single_information)
        router_builder.add_node("AskCompletenessQuestion", ask_completeness_question)
        router_builder.add_node("SuggestQuestion", suggest_question)
        router_builder.add_node("CorrectnessEvaluator", correctness_evaluator)
        router_builder.add_node("FixValue", fix_value)
        router_builder.add_node("AskCorrectnessQuestion", ask_correctness_question)

        # Add edges to connect nodes
        router_builder.add_edge(START, "route_completeness")
        router_builder.add_conditional_edges(
            "route_completeness", route_completeness,
            {
                "ExtractSingleInformation": "ExtractSingleInformation",
                "Pass": "CorrectnessEvaluator"
            },
        )
        router_builder.add_conditional_edges(
            "ExtractSingleInformation", completeness_inner_route,
            {
                "AskCompletenessQuestion": "AskCompletenessQuestion",
                "SuggestQuestion": "SuggestQuestion",
                "Pass": "route_completeness"
            },
        )
        router_builder.add_edge("AskCompletenessQuestion", END)
        router_builder.add_edge("SuggestQuestion", END)
        router_builder.add_conditional_edges(
            "CorrectnessEvaluator", route_correctness,
            {
                "FixValue": "FixValue",
                "AskCorrectnessQuestion": "AskCorrectnessQuestion",
                "Pass": END
            })
        router_builder.add_edge("FixValue", END)
        router_builder.add_edge("AskCorrectnessQuestion", END)

        # Compile
        chain = router_builder.compile()

        png_data = chain.get_graph().draw_mermaid_png(max_retries=5, retry_delay=2.0)

        with open("workflow.png", "wb") as f:
            f.write(png_data)

        print("Workflow image saved as workflow.png")


if __name__ == '__main__':
    user_input = ("When we see bad news for BTC and the price is lower than 58k. "
             "Use less than 2% of the portofolio."
             "Sell when the price of BTC is 10% on the upside or more, but remember to sell the"
             "position out if price falls more than 15%.")
    agent = TradePlanEvaluatorAgent()
