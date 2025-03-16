

def lambda_handler(event, context):
    print(f'{event=}')

    return {'statusCode': 200, 'body': f'Done.'}

