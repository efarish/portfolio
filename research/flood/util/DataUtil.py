import boto3
import pandas as pd
from io import BytesIO


class DataUtil:
    """
    Utility class used for retrieving files form AWS S3.
    """

    def __init__(self, project_bucket,
                 train_bucket,
                 train_file,
                 target_variable,
                 test_file=None):

        self.target_variable = target_variable
        self.project_bucket = project_bucket
        self.train_bucket = train_bucket
        self.train_file = train_file
        self.test_file = test_file
        self.s3_client = boto3.client('s3')
        self.s3_resource = boto3.resource('s3')

    def get_s3_df(self, file, **kwargs):
        """
        Retrieve file from S3 bucket.
        """
        data = self.s3_client.get_object(Bucket=self.project_bucket, Key=file)['Body'].read()
        return pd.read_csv(BytesIO(data), **kwargs)

    def get_data_sagemaker(self, set_train_index=True,
                          include_original_data=True):
        """
        Return dataframes used for training. 
        """
        train = self.get_s3_df(self.train_bucket + '/' + self.train_file,)
        if set_train_index:
            train.set_index('id', inplace=True)
        target_field = train.pop(self.target_variable)
        train.insert(0, self.target_variable, target_field)
        orig = None
        if include_original_data:
            orig = self.get_s3_df(self.train_bucket + '/train_original.csv',)
            target_field = orig.pop(self.target_variable)
            orig.insert(0, self.target_variable, target_field)
        test = None
        if self.test_file is not None:
            test = self.get_s3_df(self.train_bucket + '/' + self.test_file,)
            test.set_index('id', inplace=True)
        return {'train': train, 'test': test, 'orig': orig}
