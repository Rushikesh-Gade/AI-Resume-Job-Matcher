"""
Script to create DynamoDB tables
"""
import boto3
from dynamodb_schema import (
    USERS_TABLE_SCHEMA,
    RESUMES_TABLE_SCHEMA,
    JOBS_TABLE_SCHEMA,
    MATCHES_TABLE_SCHEMA,
    APPLICATIONS_TABLE_SCHEMA
)

dynamodb = boto3.client('dynamodb', region_name='ap-south-1')


def create_table(schema):
    """Create a DynamoDB table"""
    try:
        response = dynamodb.create_table(**schema)
        print(f"Creating table {schema['TableName']}...")
        return response
    except dynamodb.exceptions.ResourceInUseException:
        print(f"Table {schema['TableName']} already exists")
    except Exception as e:
        print(f"Error creating table {schema['TableName']}: {str(e)}")


def main():
    """Create all tables"""
    print("Starting table creation...")
    
    create_table(USERS_TABLE_SCHEMA)
    create_table(RESUMES_TABLE_SCHEMA)
    create_table(JOBS_TABLE_SCHEMA)
    create_table(MATCHES_TABLE_SCHEMA)
    create_table(APPLICATIONS_TABLE_SCHEMA)
    
    print("All tables created successfully!")


if __name__ == '__main__':
    main()
