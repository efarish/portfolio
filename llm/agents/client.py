from AgentSupervisor import AgentSupervisor
import logging as log

"""
A client of the AgentSupervisor class.
"""

log.getLogger().setLevel(log.WARN)

if __name__ == "__main__":
    agent_supervisor = AgentSupervisor()

    # Examples requests:
    request = "Retreieve the NYC reservior levels."
    # request="Create a salutaion for my mother."
    # request="Write a salutation to my wife. Then retreieve the NYC reservior levels."
    response = agent_supervisor.make_request(request)
    for idx, message in enumerate(response):
        print(f"{idx}. {message}")
        print("---")
