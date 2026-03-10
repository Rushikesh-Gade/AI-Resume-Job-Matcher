"""
Lambda function to track job applications
"""
import json
import boto3
import os
import uuid
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
APPLICATIONS_TABLE = os.getenv('DYNAMODB_APPLICATIONS_TABLE', 'ResumeMatcherApplications')


def create_application(event):
    """Create new job application record"""
    try:
        body = json.loads(event['body'])
        user_id = event['requestContext']['authorizer']['user_id']
        
        application_id = str(uuid.uuid4())
        
        table = dynamodb.Table(APPLICATIONS_TABLE)
        table.put_item(
            Item={
                'application_id': application_id,
                'user_id': user_id,
                'job_id': body['job_id'],
                'job_title': body.get('job_title', ''),
                'company': body.get('company', ''),
                'status': 'Applied',
                'applied_at': datetime.utcnow().isoformat(),
                'notes': body.get('notes', '')
            }
        )
        
        return {
            'statusCode': 201,
            'body': json.dumps({
                'message': 'Application tracked successfully',
                'application_id': application_id
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }


def get_user_applications(event):
    """Get all applications for a user"""
    try:
        user_id = event['requestContext']['authorizer']['user_id']
        
        table = dynamodb.Table(APPLICATIONS_TABLE)
        response = table.query(
            IndexName='UserApplicationsIndex',
            KeyConditionExpression='user_id = :uid',
            ExpressionAttributeValues={':uid': user_id},
            ScanIndexForward=False
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'applications': response['Items'],
                'count': len(response['Items'])
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }


def update_application_status(event):
    """Update application status"""
    try:
        application_id = event['pathParameters']['id']
        body = json.loads(event['body'])
        new_status = body['status']
        
        table = dynamodb.Table(APPLICATIONS_TABLE)
        table.update_item(
            Key={'application_id': application_id},
            UpdateExpression='SET #status = :status, updated_at = :updated',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={
                ':status': new_status,
                ':updated': datetime.utcnow().isoformat()
            }
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Status updated successfully'})
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }


def lambda_handler(event, context):
    """Main Lambda handler for application tracking"""
    http_method = event['httpMethod']
    path = event['path']
    
    if http_method == 'POST' and path == '/applications':
        return create_application(event)
    elif http_method == 'GET' and path == '/applications':
        return get_user_applications(event)
    elif http_method == 'PUT' and '/applications/' in path:
        return update_application_status(event)
    else:
        return {
            'statusCode': 404,
            'body': json.dumps({'error': 'Not found'})
        }
