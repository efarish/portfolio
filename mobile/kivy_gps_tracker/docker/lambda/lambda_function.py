import boto3
import requests


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
    response = requests.get(url, headers=request_header, timeout=5)

    if(not response.ok):
        print(f'Error: {response.status_code}')
        return {"isAuthorized": False}

    return {"isAuthorized": True}

def lambda_handler_connect(event, context):

    headers = event['headers']

    if('authorization' not in headers):
        print('No Authorization header')
        return {"statusCode": 401, 'body': 'User not authorized.'}
    
    connectionId = headers['connectionId']

    api = get_api()

    # The code below assumes the string in headers['authorization'] begins with "Bearer".
    request_header = {"Authorization": f"{headers['authorization']}", "Content-Type": "application/json"}
    url = api + '/websoc/connect'
    print(f'{url=}')
    response = requests.post(url, json={'connectionId': connectionId}, headers=request_header, timeout=5)

    if(not response.ok):
        print(f'Error: {response.status_code}, {response.text}')
        return {'statusCode': response.status_code, 'body': response.text}

    return {'statusCode': 201, 'body': 'Connected.'} 

def lambda_handler_disconnect(event, context):

    headers = event['headers']

    if('authorization' not in headers):
        print('No Authorization header')
        return {"statusCode": 401, 'body': 'User not authorized.'}
    
    connectionId = headers['connectionId']

    api = get_api()

    # The code below assumes the string in headers['authorization'] begins with "Bearer".
    request_header = {"Authorization": f"{headers['authorization']}", "Content-Type": "application/json"}
    url = api + '/websoc/disconnect'
    print(f'{url=}')
    response = requests.post(url, json={'connectionId': connectionId}, headers=request_header, timeout=5)

    if(not response.ok):
        print(f'Error: {response.status_code}, {response.text}')
        return {'statusCode': response.status_code, 'body': response.text}

    return {'statusCode': 201, 'body': 'disconnected.'} 
