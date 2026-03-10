"""
Lambda function to send email notifications for high-match jobs
"""
import json
import boto3
import os
from datetime import datetime

ses_client = boto3.client('ses', region_name=os.getenv('SES_REGION', 'ap-south-1'))
dynamodb = boto3.resource('dynamodb')

USERS_TABLE = os.getenv('DYNAMODB_USERS_TABLE', 'ResumeMatcherUsers')
MATCHES_TABLE = os.getenv('DYNAMODB_MATCHES_TABLE', 'ResumeMatcherMatches')
SENDER_EMAIL = os.getenv('SES_SENDER_EMAIL', 'noreply@resumematcher.com')
HIGH_MATCH_THRESHOLD = int(os.getenv('HIGH_MATCH_THRESHOLD', '70'))


def get_user_email(user_id):
    """Get user email from DynamoDB"""
    table = dynamodb.Table(USERS_TABLE)
    response = table.get_item(Key={'user_id': user_id})
    
    if 'Item' in response:
        return response['Item'].get('email')
    return None


def send_match_notification(user_email, matches):
    """Send email notification for high-match jobs"""
    
    # Build email body
    job_list = ""
    for match in matches:
        job_list += f"""
        - {match['job_title']} at {match['company']}
          Match Score: {match['match_score']}%
          {match['explanation']}
        
        """
    
    email_body = f"""
    Hello,
    
    Great news! We found {len(matches)} job(s) that match your profile with a score of {HIGH_MATCH_THRESHOLD}% or higher:
    
    {job_list}
    
    Log in to your account to view full details and apply to these positions.
    
    Best regards,
    AI Resume Job Matcher Team
    """
    
    subject = f"🎯 {len(matches)} New Job Match{'es' if len(matches) > 1 else ''} Found!"
    
    try:
        response = ses_client.send_email(
            Source=SENDER_EMAIL,
            Destination={'ToAddresses': [user_email]},
            Message={
                'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                'Body': {'Text': {'Data': email_body, 'Charset': 'UTF-8'}}
            }
        )
        
        return response['MessageId']
        
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        raise


def lambda_handler(event, context):
    """
    Main Lambda handler for sending notifications
    
    Expected event format:
    {
        "user_id": "user123",
        "matches": [
            {
                "job_id": "job456",
                "job_title": "Software Engineer",
                "company": "Tech Corp",
                "match_score": 85,
                "explanation": "Strong match..."
            }
        ]
    }
    """
    try:
        user_id = event['user_id']
        matches = event.get('matches', [])
        
        # Filter high-match jobs
        high_matches = [m for m in matches if m.get('match_score', 0) >= HIGH_MATCH_THRESHOLD]
        
        if not high_matches:
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'No high-match jobs to notify',
                    'threshold': HIGH_MATCH_THRESHOLD
                })
            }
        
        # Get user email
        user_email = get_user_email(user_id)
        
        if not user_email:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'User email not found'})
            }
        
        # Send notification
        message_id = send_match_notification(user_email, high_matches)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Notification sent successfully',
                'email': user_email,
                'matches_count': len(high_matches),
                'message_id': message_id
            })
        }
        
    except Exception as e:
        print(f"Error sending notification: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
