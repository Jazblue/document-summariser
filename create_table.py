import boto3

dynamodb = boto3.resource(
    "dynamodb",
    endpoint_url="http://localhost:8000",
    region_name="us-west-2",
    aws_access_key_id="fakeMyKeyId",
    aws_secret_access_key="fakeSecretAccessKey"
)

# Create a table
table_name = "documents"

existing_tables = [t.name for t in dynamodb.tables.all()]
if table_name in existing_tables:
    print(f"Table '{table_name}' already exists.")
else:
    table = dynamodb.create_table(
        TableName=table_name,
        KeySchema=[
            {"AttributeName": "doc_id", "KeyType": "HASH"}  # Partition key
        ],
        AttributeDefinitions=[
            {"AttributeName": "doc_id", "AttributeType": "S"}
        ],
        BillingMode="PAY_PER_REQUEST"
    )
    table.wait_until_exists()
    print(f"Table '{table_name}' created successfully!")
