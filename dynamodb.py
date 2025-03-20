import boto3
import os
import time
# Initialize the DynamoDB client
dynamodb = boto3.client('dynamodb', region_name='us-east-1',
                        aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
                        aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'])

# Define the table name and schema
# Define the table name and schema
table_name = 'Students'
key_schema = [
    {
        'AttributeName': 'id',
        'KeyType': 'HASH'  # Partition key
    }
]
attribute_definitions = [
    {
        'AttributeName': 'id',
        'AttributeType': 'N'  # Number
    },
    {
        'AttributeName': 'name',
        'AttributeType': 'S'  # String
    }
]
provisioned_throughput = {
    'ReadCapacityUnits': 5,
    'WriteCapacityUnits': 5
}

# Create the table
response = dynamodb.create_table(
    TableName=table_name,
    KeySchema=key_schema,
    AttributeDefinitions=attribute_definitions,  # Include 'name' attribute
    ProvisionedThroughput=provisioned_throughput,
    GlobalSecondaryIndexes=[
        {
            'IndexName': 'NameIndex',
            'KeySchema': [
                {
                    'AttributeName': 'name',
                    'KeyType': 'HASH'  # Partition key
                }
            ],
            'Projection': {
                'ProjectionType': 'ALL'
            },
            'ProvisionedThroughput': {
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        }
    ]
)


# response.wait_until_exists()
# Wait for the table to be created
# dynamodb.get_waiter('table_exists').wait(TableName=table_name)

# Print the response
print(response)
time.sleep(20)
print("Table created:", response)

# Define the data to be inserted
data = [
    {
        "id": {"N": '1'},
        "name": {"S": "mr_bean"},
        "major": {"S": "lawyer"},
        "year": {"S": "freshmen"}
    },
    {
        "id": {"N": '2'},
        "name": {"S": "president_biden"},
        "major": {"S": "history"},
        "year": {"S": "sophomore"}
    },
    {
        "id": {"N": '3'},
        "name": {"S": "vin_diesel"},
        "major": {"S": "computer_science"},
        "year": {"S": "sophomore"}
    },
    {
        "id": {"N": '4'},
        "name": {"S": "floki"},
        "major": {"S": "history"},
        "year": {"S": "junior"}
    },
    {
        "id": {"N": '5'},
        "name": {"S": "president_trump"},
        "major": {"S": "physics"},
        "year": {"S": "junior"}
    },
    {
        "id": {"N": '6'},
        "name": {"S": "morgan_freeman"},
        "major": {"S": "math"},
        "year": {"S": "senior"}
    },
    {
        "id": {"N": '7'},
        "name": {"S": "president_obama"},
        "major": {"S": "electrical_engineering"},
        "year": {"S": "senior"}
    },
    {
        "id": {"N": '8'},
        "name": {"S": "johnny_dep"},
        "major": {"S": "computer_science"},
        "year": {"S": "senior"}
    }
]

# Insert data into the DynamoDB table

for item in data:
    dynamodb.put_item(TableName=table_name, Item=item)

print("Data inserted into the DynamoDB table.")
