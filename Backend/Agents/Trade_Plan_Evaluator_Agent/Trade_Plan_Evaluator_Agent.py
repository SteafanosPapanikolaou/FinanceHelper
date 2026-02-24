from pydantic import BaseModel, Field
from langchain.agents import create_agent
from Backend.Connectors.LLM_Connector import LLMConnector
from typing import Optional, Any, Literal
from datetime import datetime


class FieldState(BaseModel):
    value: Any = None
    completeness_confidence: float  = 0.0
    completeness_question: str
    correctness_confidence: float  = 0.0
    source: Literal["user", "inferred", "corrected"]  = None
    timestamp: datetime  = None
    iteration: int  = 0

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

model='qwen3:1.7b'
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
state["entry_point"].value = '58000'
state["stop_loss"].value = '15%'
state["take_profit"].value = '10%'
state["position_size"].value = None

for subject in state.keys():

    if state[subject].value == None:
        print(subject, state[subject].value)
        completeness_prompt = f"Extract information about {subject}."
        question_prompt = completeness_prompt

        reflection_prompt = f"""
        User input:
        {user_input}
        
        {question_prompt}
        """

        agent = create_agent(
            model=llm,
            system_prompt="""
                            You are a financial information extraction system.
                            
                            Extract ONLY relevant information.
                            
                            If the value is missing, output null.
                            
                            Never infer or guess.
                            
                            Missing means null.
                            """
        )

        result = agent.invoke({
            "messages": [{"role": "user", "content": reflection_prompt}],
        })

        print(result['messages'][-1].content)
