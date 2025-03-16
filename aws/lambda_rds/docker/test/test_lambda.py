
import lambda_function
from util import mock_get_db


def test_lambda_1():

    lambda_function.get_db = mock_get_db

    lambda_function.lambda_handler(None, None)
