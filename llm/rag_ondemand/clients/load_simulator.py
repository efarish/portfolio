import concurrent.futures as cf

import requests

API = 'https://3u0mxm98r9.execute-api.us-east-1.amazonaws.com' 


def f(query):
    """Submit query."""  

    # Get a session.
    urlCreateSession = API + '/create_session'
    response = requests.get(urlCreateSession)
    session_id = response.json()['session_id']
    print(f'Session Id: {session_id}')

    # Upload file.
    file_path = './data/2505.10543.pdf'
    urlUpload = API + '/upload'
    with open(file_path, 'rb') as doc_file:
        data = {"session_id": session_id}
        files = {"file": (file_path, doc_file)}
        response = requests.post(urlUpload, data=data, files=files)
        if response.status_code != 200:
            print("Upload image failed:", response.status_code) 

    # Prepare index.
    urlPrepare = API + '/prepare'
    data = {"session_id": session_id, "recreate": False}
    response = requests.post(urlPrepare, json=data)
    if response.status_code != 200:
        print("Prepare failed:", response.status_code) 

    # Submit query.
    urlQuery = API + '/query'
    data = {"session_id": session_id, "query": "Summarize the document."}
    response = requests.post(urlQuery, json=data)
    print("Done:", session_id, response.text)



def runner(query):
    return query, f(query)

def make_dict(queries):
    with cf.ProcessPoolExecutor(max_workers=len(queries)) as e:
        futures = [e.submit(runner, s) for s in queries]
        d = dict(f.result() for f in cf.as_completed(futures))
        return d


if __name__ == "__main__":
    max_workers = 1
    queries = ["Summarize the document."] * max_workers
    make_dict(queries)
