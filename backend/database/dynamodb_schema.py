"""
DynamoDB table schemas for AI Resume Job Matcher
"""

USERS_TABLE_SCHEMA = {
    'TableName': 'ResumeMatcherUsers',
    'KeySchema': [
        {'AttributeName': 'user_id', 'KeyType': 'HASH'}
    ],
    'AttributeDefinitions': [
        {'AttributeName': 'user_id', 'AttributeType': 'S'},
        {'AttributeName': 'email', 'AttributeType': 'S'}
    ],
    'GlobalSecondaryIndexes': [
        {
            'IndexName': 'EmailIndex',
            'KeySchema': [
                {'AttributeName': 'email', 'KeyType': 'HASH'}
            ],
            'Projection': {'ProjectionType': 'ALL'},
            'ProvisionedThroughput': {
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        }
    ],
    'BillingMode': 'PAY_PER_REQUEST'
}

RESUMES_TABLE_SCHEMA = {
    'TableName': 'ResumeMatcherResumes',
    'KeySchema': [
        {'AttributeName': 'user_id', 'KeyType': 'HASH'}
    ],
    'AttributeDefinitions': [
        {'AttributeName': 'user_id', 'AttributeType': 'S'}
    ],
    'BillingMode': 'PAY_PER_REQUEST'
}

JOBS_TABLE_SCHEMA = {
    'TableName': 'ResumeMatcherJobs',
    'KeySchema': [
        {'AttributeName': 'job_id', 'KeyType': 'HASH'}
    ],
    'AttributeDefinitions': [
        {'AttributeName': 'job_id', 'AttributeType': 'S'},
        {'AttributeName': 'source', 'AttributeType': 'S'},
        {'AttributeName': 'scraped_at', 'AttributeType': 'S'}
    ],
    'GlobalSecondaryIndexes': [
        {
            'IndexName': 'SourceIndex',
            'KeySchema': [
                {'AttributeName': 'source', 'KeyType': 'HASH'},
                {'AttributeName': 'scraped_at', 'KeyType': 'RANGE'}
            ],
            'Projection': {'ProjectionType': 'ALL'},
            'ProvisionedThroughput': {
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        }
    ],
    'BillingMode': 'PAY_PER_REQUEST'
}

MATCHES_TABLE_SCHEMA = {
    'TableName': 'ResumeMatcherMatches',
    'KeySchema': [
        {'AttributeName': 'user_id', 'KeyType': 'HASH'},
        {'AttributeName': 'job_id', 'KeyType': 'RANGE'}
    ],
    'AttributeDefinitions': [
        {'AttributeName': 'user_id', 'AttributeType': 'S'},
        {'AttributeName': 'job_id', 'AttributeType': 'S'},
        {'AttributeName': 'match_score', 'AttributeType': 'N'}
    ],
    'GlobalSecondaryIndexes': [
        {
            'IndexName': 'ScoreIndex',
            'KeySchema': [
                {'AttributeName': 'user_id', 'KeyType': 'HASH'},
                {'AttributeName': 'match_score', 'KeyType': 'RANGE'}
            ],
            'Projection': {'ProjectionType': 'ALL'},
            'ProvisionedThroughput': {
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        }
    ],
    'BillingMode': 'PAY_PER_REQUEST'
}

APPLICATIONS_TABLE_SCHEMA = {
    'TableName': 'ResumeMatcherApplications',
    'KeySchema': [
        {'AttributeName': 'application_id', 'KeyType': 'HASH'}
    ],
    'AttributeDefinitions': [
        {'AttributeName': 'application_id', 'AttributeType': 'S'},
        {'AttributeName': 'user_id', 'AttributeType': 'S'},
        {'AttributeName': 'applied_at', 'AttributeType': 'S'}
    ],
    'GlobalSecondaryIndexes': [
        {
            'IndexName': 'UserApplicationsIndex',
            'KeySchema': [
                {'AttributeName': 'user_id', 'KeyType': 'HASH'},
                {'AttributeName': 'applied_at', 'KeyType': 'RANGE'}
            ],
            'Projection': {'ProjectionType': 'ALL'},
            'ProvisionedThroughput': {
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        }
    ],
    'BillingMode': 'PAY_PER_REQUEST'
}
