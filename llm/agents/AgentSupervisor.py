import operator
from typing import (
    Annotated,
    Sequence,
    TypedDict,
)

from dotenv import load_dotenv
from langchain.agents import (
    create_openai_tools_agent,
    create_react_agent,
    tool,
)
from langchain.output_parsers.openai_functions import JsonOutputFunctionsParser
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import END, StateGraph

import Agents
import util
from Agents import Agents


class AgentState(TypedDict):
    """A LangGraph state class. 

    Args:
        TypedDict
    """

    messages: Annotated[Sequence[BaseMessage], operator.add]
    nextAgent: str


class AgentSupervisor:
    """
    A class managing request to two agents:
    - An agent to write salutations to family members.
    - An agent to get the current NYC reservior levels.
    """

    def __init__(self) -> None:
        self.agents = Agents()
        self.route_options = ["FINISH"] + self.agents.get_names()
        self.create_chain()
        self.create_graph()

    def create_chain(self):
        """
        Create the LangChain chain use to process requests made by clients.
        """
        self.system_prompt = (
            "You are a supervisor tasked with managing a conversation between the"
            " following workers: {agents}. Given the following user requests,"
            " respond with the worker to act next. Each worker will perform a"
            " task and respond with their results and status. When finished,"
            " respond with FINISH."
        )
        self.function_def = {
            "name": "route",
            "description": "Select the next agent.",
            "parameters": {
                "title": "routeSchema",
                "type": "object",
                "properties": {
                    "nextAgent": {
                        "title": "Next Agent",
                        "anyOf": [
                            {"enum": self.route_options},
                        ],
                    }
                },
                "required": ["nextAgent"],
            },
        }
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self.system_prompt),
                MessagesPlaceholder(variable_name="messages"),
                (
                    "system",
                    "Given the conversation above, who should act next?"
                    " Or should we FINISH? Select one of: {routeOptions}",
                ),
            ]
        ).partial(
            routeOptions=str(", ".join(self.route_options)),
            agents=", ".join(self.agents.get_names()),
        )

        self.llm = util.get_llm_model()

        self.supervisor_chain = (
            prompt
            | self.llm.bind_functions(
                functions=[self.function_def], function_call="route"
            )
            | JsonOutputFunctionsParser()
        )

    def create_graph(self):
        """
        Creates the graph of agents that will be responding to requests.
        """
        workflow = StateGraph(AgentState)
        workflow.add_node("supervisor", self.supervisor_chain)

        for agent in self.agents.get_agents():
            workflow.add_node(agent.get_name(), agent)

        for agent in self.agents.get_agents():
            workflow.add_edge(agent.get_name(), "supervisor")

        conditional_map = {k: k for k in self.agents.get_names()}
        conditional_map["FINISH"] = END
        workflow.add_conditional_edges(
            "supervisor", lambda x: x["nextAgent"], conditional_map
        )
        workflow.set_entry_point("supervisor")
        self.graph = workflow.compile()

    def make_request(self, request: str) -> str:
        """
        Method used by clients to make requests.

        Args:
            request (str)

        Returns:
            str
        """
        state = self.graph.invoke({"messages": [HumanMessage(content=request)]})
        messages = []
        for message in state["messages"]:
            messages.append(message.content)
        return messages
