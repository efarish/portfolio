import boto3
import pandas as pd
from io import BytesIO

class DataUtil:
    def __init__(self, project_bucket,
                 train_bucket,
                 train_file,
                 test_file=None):

        self.project_bucket = project_bucket
        self.train_bucket = train_bucket
        self.train_file = train_file
        self.test_file = test_file
        self.s3_client = boto3.client('s3')
        self.s3_resource = boto3.resource('s3')

    def get_s3_df(self, file, **kwargs):
        data = self.s3_client.get_object(Bucket=self.project_bucket, Key=file)['Body'].read()
        return pd.read_csv(BytesIO(data), **kwargs)

    def get_data_sagemaker(self):
        train = self.get_s3_df(self.train_bucket + '/' + self.train_file,)
        test = None
        if self.test_file is not None:
            test = self.get_s3_df(self.train_bucket + '/' + self.test_file,)
            test.set_index('id', inplace=True)
        return {'train': train, 'test': test}

