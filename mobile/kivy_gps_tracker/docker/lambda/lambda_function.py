import json

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

    print(f"api=")

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

    if('authorization' not in headers):
        print('No Authorization header')
        return {"statusCode": 401, 'body': 'User not authorized.'}
    
    connectionId = event['requestContext']['connectionId']

    api = get_api()

    # The code below assumes the string in headers['authorization'] begins with "Bearer".
    request_header = {"Authorization": f"{headers['authorization']}", "Content-Type": "application/json"}
    url = f'{api}/websoc/{action_type}'
    print(f'{url=}')
    response = get_client().post(url, json={'connectionId': connectionId}, headers=request_header, timeout=5)

    if(response.status_code != 201):
        print(f'Error: {response.status_code}, {response.text}')
        return {'statusCode': response.status_code, 'body': response.text}

    return {'statusCode': 201, 'body': 'Connected.'} 

def handle_update_location(event, context):

    headers = event['headers']

    if('authorization' not in headers):
        print('No Authorization header')
        return {"statusCode": 401, 'body': 'User not authorized.'}
    
    connectionId = event['requestContext']['connectionId']

    api = get_api()

    # The code below assumes the string in headers['authorization'] begins with "Bearer".
    request_header = {"Authorization": f"{headers['authorization']}", "Content-Type": "application/json"}
    url = api + '/websoc/get_websocket_ids'
    print(f'{url=}')
    response = get_client().post(url, json={'connectionId': connectionId}, headers=request_header, timeout=5)

    if(response.status_code != 200):
        print(f'Error: {response.status_code}, {response.text}')
        return {'statusCode': response.status_code, 'body': response.text}
    else:
        print(f'{response=}')

    web_soc_ids = response.json()
    print(f'{web_soc_ids=}')

    user_location = event['body'].decode('utf-8')
    print(f'{user_location=}')

    #s3 = boto3.resource('s3')
    #config_json = s3.Object('a-unique-public-bucket-name', 'config.json').get()['Body'].read().decode('utf-8')  
    #config = json.loads(config_json)  
    #ws_call_back = config['config']['web_socket_callback']   
    domain_name = event["requestContext"]["domainName"]
    stage = event["requestContext"]["stage"]
    ws_call_back = f"https://{domain_name}/{stage}"
    print(f'{ws_call_back=}')

    if len(web_soc_ids) > 0:
        client = boto3.client('apigatewaymanagementapi', endpoint_url=ws_call_back) 
        message=user_location.encode('utf-8')
        for id in web_soc_ids:
            response = client.post_to_connection(ConnectionId=id, Data=message)
            print(response)
    else: print('No connections to broadcast to.')

    return {'statusCode': 201, 'body': 'Location updated.'}

def lambda_handler_websocket(event, context):
    print(f'event=')
    event_type = event["requestContext"]["eventType"]
    if event_type == 'CONNECT':
        return handle_conn_disc(event, context, 'connect')
    elif event_type == 'DISCONNECT': 
        return handle_conn_disc(event, context, 'disconnect')
    elif event_type == 'MESSAGE':
        return handle_update_location(event, context)
    else:
        return {'statusCode': 400, 'body': f'Invalid event type: {event_type}.'}

