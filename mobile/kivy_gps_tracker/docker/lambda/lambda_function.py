import boto3
import requests


def get_client():
    return requests

def get_api():

    client = boto3.client('servicediscovery', 
        region_name='us-east-1', 
        endpoint_url='https://servicediscovery.us-east-1.amazonaws.com')

    response = client.discover_instances(
        HealthStatus='ALL',
        NamespaceName='ecs-tracker-cluster-api-namespace', 
        ServiceName='ecs-tracker-cluster-api-discovery-service')
    
    if not response['Instances'] or len(response['Instances']) == 0:
        print('No service instances found')
        return {"isAuthorized": False}
       
    instance = response['Instances'][0]
    ip_address = instance['Attributes']['AWS_INSTANCE_IPV4']
    port = instance['Attributes']['AWS_INSTANCE_PORT'] 

    api = f'http://{ip_address}:{port}'

    print(f"{api=}")

    return api    


def lambda_handler_auth(event, context):

    headers = event['headers']

    if('authorization' not in headers):
        print('No Authorization header')
        return {"isAuthorized": False}

    api = get_api()

    # The code below assumes the string in headers['authorization'] begins with "Bearer".
    request_header = {"Authorization": f"{headers['authorization']}", "Content-Type": "application/json"}
    url = api + '/auth/check_token'
    print(f'{url=}')
    response = get_client().get(url, headers=request_header, timeout=5)

    if(response.status_code != 200):
        print(f'Error: {response.status_code}')
        return {"isAuthorized": False}

    return {"isAuthorized": True}

def handle_conn_disc(event, context, action_type):

    headers = event['headers']

    if(action_type == 'connect' and 'Authorization' not in headers):
        print('No Authorization header')
        return {"statusCode": 401, 'body': 'User not authorized.'}
    
    connectionId = event['requestContext']['connectionId']

    api = get_api()
    url = f'{api}/websoc/{action_type}'
    print(f'{url=}')

    # The code below assumes the string in headers['authorization'] begins with "Bearer".
    if action_type == 'connect':
        request_header = {"Authorization": f"{headers['Authorization']}", "Content-Type": "application/json"}
        print(f'{request_header=}')
        response = get_client().post(url, json={'connectionId': connectionId}, headers=request_header, timeout=5)
    else: 
        response = get_client().post(url, json={'connectionId': connectionId}, timeout=5)

    if(response.status_code != 201):
        print(f'Error: {response.status_code}, {response.text}')
        return {'statusCode': response.status_code, 'body': response.text}

    return {'statusCode': 201, 'body': 'Connected.'} 

def handle_update_location(event, context):
  
    connectionId = event['requestContext']['connectionId']
    user_location = event['body']
    print(f'{user_location=}')
    domain_name = event["requestContext"]["domainName"]
    stage = event["requestContext"]["stage"]
    ws_call_back = f"https://{domain_name}/{stage}"
    print(f'{ws_call_back=}')    

    api = get_api()
    url = api + '/websoc/update_location'
    print(f'{url=}')

    response = get_client().post(url, 
                                 json={'connectionId': connectionId, 
                                       'location': user_location,
                                       'callback': ws_call_back}, 
                                 timeout=5) 

    if(response.status_code != 200):
        print(f'Error: {response.status_code}, {response.text}')
        return {'statusCode': response.status_code, 'body': response.text}
    else:
        print(f'{response=}')

    web_soc_ids = response.json()
    print(f'{web_soc_ids=}')

    return {'statusCode': 201, 'body': 'Location updated.'}

def lambda_handler_websocket(event, context):
    print(f'{event=}')
    event_type = event["requestContext"]["eventType"]
    if event_type == 'CONNECT':
        return handle_conn_disc(event, context, 'connect')
    elif event_type == 'DISCONNECT': 
        return handle_conn_disc(event, context, 'disconnect')
    elif event_type == 'MESSAGE':
        return handle_update_location(event, context)
    else:
        return {'statusCode': 400, 'body': f'Invalid event type: {event_type}.'}

