from pydantic import BaseModel, Field
from langchain.agents import create_agent
from Backend.Connectors.LLM_Connector import LLMConnector
from typing import Any, Literal
from datetime import datetime


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


state = {
    "entry_condition": FieldState(completeness_question="Buy when news are positive?"),
    "entry_point": FieldState(completeness_question="Buy in at the current price?"),
    "stop_loss": FieldState(completeness_question="10% of the entry point?"),
    "take_profit": FieldState(completeness_question="15% of the entry point?"),
    "position_size": FieldState(completeness_question="2% of portofolio?"),
}

model = 'qwen3:4b'
llm = LLMConnector.llm_connect(model=model)
agent = create_agent(
    model=llm,
    response_format=TradingPlan,
    system_prompt="""
You are a financial information extraction system.

Extract ONLY explicitly stated values.

If the value is missing, output null.

Never infer or guess.

Missing means null.
"""
)

user_input = ("When we see bad news for BTC and the price is lower than 58k. "
             "Use less than 2% of the portofolio."
             "Sell when the price of BTC is 10% on the upside or more, but remember to sell the"
             "position out if price falls more than 15%.")

# result = agent.invoke({
#     "messages": [{"role": "user", "content": user_input}],
# })

# plan = result["structured_response"].model_dump()

# for key, value in plan.items():
#     if key in state:
#         state[key].value = value

# for i in state.keys():
#     print(i,":", state[i].value)

state["entry_condition"].value = None
state["entry_condition"].value = ("entry_condition: "
                                  "- BTC and the price is lower than 58k "
                                  "exit_conditions: "
                                  "- Sell when the price of BTC is 10% on the upside or more "
                                  "- Sell the position out if price falls more than 15%.")
state["entry_point"].value = '58000'
state["stop_loss"].value = '15%'
state["take_profit"].value = '10%'
state["position_size"].value = None
state["position_size"].value = "Position Size: Less than 2% of portfolio."
model = 'granite4:3b'
llm = LLMConnector.llm_connect(model=model)
for subject in state.keys():

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

    if state[subject].value is not None:
        print('Working on correctness')
        print(subject, state[subject].value)


        class CheckCorrectnessPlan(BaseModel):
            clarification_question: str | None = Field(default=None, description="Clarification Question")
            correctness_confidence: float = Field(default=0.0, description="Evaluation confidence")

        correctness_prompt = f"""
Subject in question:
{subject}

User input:
{user_input}

Extracted output:
{state[subject].value}
"""

        agent = create_agent(
            model=llm,
            response_format=CheckCorrectnessPlan,
            system_prompt="""
You are going to evaluate the Extracted output from the User input for the Subject in question.

Output an Evaluation confidence from 0 to 100.

If the Output less than 80.
Create a Clarification Question for the user.

If the Output more than 80.
Return null
"""
        )

        result = agent.invoke({
            "messages": [{"role": "user", "content": correctness_prompt}],
        })

        # print(result['messages'][-1].content)
        # print(result["structured_response"])
        # print()

        state[subject].correctness_confidence = result["structured_response"].correctness_confidence
        state[subject].completeness_question = result["structured_response"].clarification_question

for i in state.keys():
    print(state[i])
    print()
