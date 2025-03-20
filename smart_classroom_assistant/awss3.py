import boto3
import os
import time


class S3:
    def __init__(self, bucket) -> None:
        self.s3_client = boto3.client('s3')
        self.s3_resouce = boto3.resource('s3')
        self.bucket = bucket

    def upload_file(self, file_name, folder=None):
        if folder is not None:
            object_name = folder + "/" + os.path.basename(file_name)
        else:
            object_name = os.path.basename(file_name)

        try:
            response = self.s3_client.upload_file(
                file_name, self.bucket, object_name)
        except Exception as e:
            print(e)
            return None
        return object_name

    def put_object(self, key, value):
        try:
            self.s3_client.put_object(Bucket=self.bucket, Key=key, Body=value)
        except Exception as e:
            print(e)

    def get_object(self, key):
        try:
            response = self.s3_client.get_object(Bucket=self.bucket, Key=key)
            return response['Body'].read()
        except Exception as e:
            print(e)
            return None


class DynamoDB:
    def __init__(self, table_name) -> None:
        self.client = boto3.client('dynamodb')
        self.table_name = table_name

    def search_by_name(self, search_name):
        expression_attribute_names = {
            '#name': 'name'
        }
        expression_attribute_values = {
            ':value': {'S': search_name}
        }

        response = self.client.query(
            TableName=self.table_name,
            IndexName='NameIndex',  # Specify the index name
            KeyConditionExpression='#name = :value',
            ExpressionAttributeNames=expression_attribute_names,
            ExpressionAttributeValues=expression_attribute_values
        )

        # Check if the item was found
        if 'Items' in response and len(response['Items']) > 0:
            item = response['Items'][0]  # Assuming the name is unique
        else:
            item = None

        return item


class CloudWatch:
    def __init__(self) -> None:
        self.log_group_name = 'app-tier'
        self.log_stream_name = 'app-logs'
        self.client = boto3.client('logs', region_name='us-east-1')

    def log_to_cloudwatch(self, message):
        # Log data to CloudWatch
        try:
            response = self.client.put_log_events(
                logGroupName=self.log_group_name,
                logStreamName=self.log_stream_name,
                logEvents=[
                    {
                        'timestamp': int(time.time() * 1000),
                        'message': message
                    },
                ]
            )

            # Check the response for errors, if needed
            if 'rejectedLogEventsInfo' in response:
                print(
                    f"Rejected log events: {response['rejectedLogEventsInfo']}")
        except Exception as e:
            print('Cloud watch error: ' + e)
