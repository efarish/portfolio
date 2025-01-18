import boto3
import requests


def lambda_handler(event, context):

    headers = event['headers']

    if('authorization' not in headers):
        print('No Authorization header')
        return {"isAuthorized": False}

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

    print(f"Service Instance: {ip_address}:{port}")

    # The code below assumes the string in headers['authorization'] begins with "Bearer".
    request_header = {"Authorization": f"{headers['authorization']}", "Content-Type": "application/json"}
    url = f'http://{ip_address}:{port}/auth/check_token'
    print(f'{url=}')
    response = requests.get(url, headers=request_header, timeout=5)

    if(not response.ok):
        print(f'Error: {response.status_code}')
        return {"isAuthorized": False}

    return {"isAuthorized": True}
