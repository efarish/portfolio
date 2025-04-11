import lambda_function


def test_health_check():

    event = {'rawPath': '/health_check'}

    lambda_function.lambda_handler(event, None)



       
