import functools
from typing import TypedDict

from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

import tools
import util


def get_chat_prompt(system_prompt: str) -> ChatPromptTemplate:
    """Create a agent chat template.

    Args:
        system_prompt (str): The system prompt used by an agent.

    Returns:
        ChatPromptTemplate
    """
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                system_prompt,
            ),
            MessagesPlaceholder(variable_name="messages"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )
    return prompt


def create_agent(llm: ChatOpenAI, tools: list, system_prompt: str) -> AgentExecutor:
    """Create an LangChain Agent Executor.

    Args:
        llm (ChatOpenAI)
        tools (list)
        system_prompt (str)

    Returns:
        AgentExecutor
    """
    prompt = get_chat_prompt(system_prompt)
    agent = create_openai_tools_agent(llm, tools, prompt)
    executor = AgentExecutor(agent=agent, tools=tools)
    return executor


def agent_node(state: dict, agent: AgentExecutor, name: str) -> dict:
    """Used by LangChain framework to call agent.

    Args:
        state (dict)
        agent (AgentExecutor)
        name (str)

    Returns:
        dict - Message to be added to the state instance.
    """
    result = agent.invoke(state)
    return {"messages": [HumanMessage(content=result["output"], name=name)]}


def create_agent_node(name: str, tools: list, system_prompt: str) -> functools.partial:
    """Create a function wrapper for an Agent Executor.

    Args:
        name (str)
        tools (list)
        system_prompt (str)

    Returns:
        functools.partial
    """
    agent = create_agent(util.get_llm_model(), tools, system_prompt)
    node = functools.partial(agent_node, agent=agent, name=name)
    return node


class Agent:
    """
    A class used to wrap a LangChain Agent Executor.
    """

    def __init__(self, name: str, tools: list, system_prompt: str) -> None:
        self.name = name
        self.default_func = create_agent_node(self.name, tools, system_prompt)

    def __call__(self, state):
        return self.default_func(state)

    def get_name(self) -> str:
        return self.name


class Agents:
    """
    Aggregator of agents. The agents created by this class will be managed by the
      AgentSupervisor class.
    """

    def __init__(self) -> None:
        salutaion = Agent(
            "SalutationWriter",
            [tools.write_a_salutation, tools.get_text_length],
            (
                "You write salutations to family members. "
                " Return both the salutation and its length by characters."
                " Use only what you know from the tools. Preface your response with,"
                " '** Here is the Salutation **'"
            ),
        )
        nycWaterLevels = Agent(
            "NewYorkReservoirAgent",
            [tools.daily_web_query],
            (
                "You retrieve NYC water levels. Preface your response with,"
                "'** The NYC reservior levels are as folows **'"
            ),
        )
        self.agents = [salutaion, nycWaterLevels]

    def get_names(self):
        return [agent.name for agent in self.agents]

    def get_agents(self):
        return self.agents


if __name__ == "__main__":
    agents = Agents()
    print(agents.get_names())
