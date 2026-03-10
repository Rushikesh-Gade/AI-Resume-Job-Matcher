"""
Lambda function to generate personalized cover letters
"""
import json
import boto3
import os
from openai import OpenAI
from datetime import datetime

s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

RESUMES_TABLE = os.getenv('DYNAMODB_RESUMES_TABLE', 'ResumeMatcherResumes')
JOBS_TABLE = os.getenv('DYNAMODB_JOBS_TABLE', 'ResumeMatcherJobs')
S3_BUCKET = os.getenv('S3_COVERLETTER_BUCKET', 'resume-matcher-coverletters')


def generate_cover_letter(resume_data, job_data):
    """Use AI to generate a personalized cover letter"""
    prompt = f"""
    Write a professional cover letter for an Indian student applying to this job.
    
    Candidate Profile:
    - Name: {resume_data.get('name', 'Candidate')}
    - Skills: {', '.join(resume_data.get('skills', []))}
    - Experience: {json.dumps(resume_data.get('experience', [])[:2], indent=2)}
    - Education: {json.dumps(resume_data.get('education', [])[:1], indent=2)}
    
    Job Details:
    - Title: {job_data.get('title')}
    - Company: {job_data.get('company')}
    - Location: {job_data.get('location', 'India')}
    
    Requirements:
    - Length: 250-400 words
    - Professional tone suitable for Indian job market
    - Highlight relevant skills and experience
    - Show enthusiasm for the role
    - Include specific examples
    - Format: Standard business letter
    
    Return only the cover letter text, no JSON or additional formatting.
    """
    
    response = openai_client.chat.completions.create(
        model=os.getenv('OPENAI_MODEL', 'gpt-4o-mini'),
        messages=[
            {"role": "system", "content": "You are a professional career counselor writing cover letters for Indian students."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=600
    )
    
    return response.choices[0].message.content.strip()


def save_cover_letter_to_s3(user_id, job_id, cover_letter_text):
    """Save cover letter to S3"""
    key = f"coverletters/{user_id}/{job_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.txt"
    
    s3_client.put_object(
        Bucket=S3_BUCKET,
        Key=key,
        Body=cover_letter_text.encode('utf-8'),
        ContentType='text/plain'
    )
    
    return key


def lambda_handler(event, context):
    """
    Main Lambda handler for cover letter generation
    
    Expected event format:
    {
        "user_id": "user123",
        "job_id": "job456"
    }
    """
    try:
        user_id = event['user_id']
        job_id = event['job_id']
        
        # Get resume data
        resumes_table = dynamodb.Table(RESUMES_TABLE)
        resume_response = resumes_table.get_item(Key={'user_id': user_id})
        
        if 'Item' not in resume_response:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Resume not found'})
            }
        
        resume_data = resume_response['Item']['parsed_data']
        
        # Get job data
        jobs_table = dynamodb.Table(JOBS_TABLE)
        job_response = jobs_table.get_item(Key={'job_id': job_id})
        
        if 'Item' not in job_response:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Job not found'})
            }
        
        job_data = job_response['Item']
        
        # Generate cover letter
        cover_letter = generate_cover_letter(resume_data, job_data)
        
        # Save to S3
        s3_key = save_cover_letter_to_s3(user_id, job_id, cover_letter)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Cover letter generated successfully',
                'job_title': job_data.get('title'),
                'company': job_data.get('company'),
                's3_key': s3_key,
                'preview': cover_letter[:200] + '...'
            })
        }
        
    except Exception as e:
        print(f"Error generating cover letter: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
