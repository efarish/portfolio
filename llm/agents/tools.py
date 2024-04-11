import logging as log

from langchain_core.tools import tool

import util

"""
Define the tools to be used by agents.

"""

@tool
def write_a_salutation(familyMemeber: str) -> str:
    """Writes a salutation to a family member"""
    log.info(f"write_a_salutation enter with {familyMemeber=}")
    salutation = (
        util.get_llm_model()
        .invoke(
            input=f"system: Your write short yet quirky salutations. Use no more than 5 workds. Write a salutation to your {familyMemeber}"
        )
        .content
    )
    log.info(f"The saluation created is: {salutation}")
    return "Input to next tool: '" + salutation + "'"


@tool
def get_text_length(text: str) -> int:
    """Returns the length of a text by characters"""
    log.info(f"get_text_length enter with {text=}")
    return str(len(text))


@tool
def daily_web_query(query: str) -> str:
    """Retrieves the NYC reservoir levels"""
    log.info(f"daily_web_query enter with {query=}")
    return "{'total_storage_Normal_capacity': '97.7', 'total_storage_Current_capacity': '99.6'"
