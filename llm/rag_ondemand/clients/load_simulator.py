# This script was used to create load on the ECS cluster
#   to test the auto-scaling feature.
#
# While testing this, notice a OpenAI RateLimitError. Below
#   is an example of the error message:
#   Rate limit reached for gpt-3.5-turbo in organization org-QTCqb2HqtDhDdhpblbV9rhTL on
#     tokens per min (TPM): Limit 200000, Used 199299, Requested 14469. Please try again in 4.13s.
#

import concurrent.futures as cf
import os

import requests

API = "https://6giv03db57.execute-api.us-east-1.amazonaws.com"


def f(query):
    """Submit query."""

    # Get a session.
    urlCreateSession = API + "/create_session"
    response = requests.get(urlCreateSession)
    session_id = response.json()["session_id"]
    print(f"Session Id: {session_id}")

    # Upload file.
    file_path = os.getcwd() + "/clients/data/2505.10543.pdf"
    urlUpload = API + "/upload"
    with open(file_path, "rb") as doc_file:
        data = {"session_id": session_id}
        files = {"file": (file_path, doc_file)}
        response = requests.post(urlUpload, data=data, files=files)
        if response.status_code != 200:
            print("Upload image failed:", response.status_code)

    # Prepare index.
    urlPrepare = API + "/prepare"
    data = {"session_id": session_id, "recreate": False}
    response = requests.post(urlPrepare, json=data)
    if response.status_code != 200:
        print("Prepare failed:", response.status_code)

    # Submit query.
    urlQuery = API + "/query"
    data = {"session_id": session_id, "query": "Summarize the document."}
    response = requests.post(urlQuery, json=data)
    print("Done:", session_id)


def runner(query):
    return query, f(query)


def make_dict(queries, max_workers):
    with cf.ProcessPoolExecutor(max_workers=max_workers) as e:
        futures = [e.submit(runner, s) for s in queries]
        d = dict(f.result() for f in cf.as_completed(futures))
        return d


if __name__ == "__main__":
    num_queries = 40
    max_workers = 10

    queries = ["Summarize the document."] * num_queries
    make_dict(queries, max_workers)
