"""
Lambda function for user authentication
"""
import json
import boto3
import os
import uuid
from datetime import datetime, timedelta
from passlib.hash import bcrypt
from jose import jwt

dynamodb = boto3.resource('dynamodb')
USERS_TABLE = os.getenv('DYNAMODB_USERS_TABLE', 'ResumeMatcherUsers')
JWT_SECRET = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'


def hash_password(password):
    """Hash password using bcrypt"""
    return bcrypt.hash(password)


def verify_password(password, hashed):
    """Verify password against hash"""
    return bcrypt.verify(password, hashed)


def generate_token(user_id, email):
    """Generate JWT token"""
    expiration = datetime.utcnow() + timedelta(hours=24)
    payload = {
        'user_id': user_id,
        'email': email,
        'exp': expiration
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def register_user(event):
    """Register a new user"""
    try:
        body = json.loads(event['body'])
        email = body['email']
        password = body['password']
        name = body.get('name', '')
        
        table = dynamodb.Table(USERS_TABLE)
        
        # Check if user exists
        response = table.query(
            IndexName='EmailIndex',
            KeyConditionExpression='email = :email',
            ExpressionAttributeValues={':email': email}
        )
        
        if response['Items']:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Email already registered'})
            }
        
        # Create user
        user_id = str(uuid.uuid4())
        hashed_password = hash_password(password)
        
        table.put_item(
            Item={
                'user_id': user_id,
                'email': email,
                'password': hashed_password,
                'name': name,
                'created_at': datetime.utcnow().isoformat(),
                'notification_enabled': True
            }
        )
        
        token = generate_token(user_id, email)
        
        return {
            'statusCode': 201,
            'body': json.dumps({
                'message': 'User registered successfully',
                'user_id': user_id,
                'token': token
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }


def login_user(event):
    """Login user"""
    try:
        body = json.loads(event['body'])
        email = body['email']
        password = body['password']
        
        table = dynamodb.Table(USERS_TABLE)
        
        # Find user by email
        response = table.query(
            IndexName='EmailIndex',
            KeyConditionExpression='email = :email',
            ExpressionAttributeValues={':email': email}
        )
        
        if not response['Items']:
            return {
                'statusCode': 401,
                'body': json.dumps({'error': 'Invalid credentials'})
            }
        
        user = response['Items'][0]
        
        # Verify password
        if not verify_password(password, user['password']):
            return {
                'statusCode': 401,
                'body': json.dumps({'error': 'Invalid credentials'})
            }
        
        token = generate_token(user['user_id'], user['email'])
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Login successful',
                'user_id': user['user_id'],
                'token': token,
                'name': user.get('name', '')
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }


def lambda_handler(event, context):
    """Main Lambda handler for authentication"""
    path = event.get('path', '')
    
    if path == '/auth/register':
        return register_user(event)
    elif path == '/auth/login':
        return login_user(event)
    else:
        return {
            'statusCode': 404,
            'body': json.dumps({'error': 'Not found'})
        }
