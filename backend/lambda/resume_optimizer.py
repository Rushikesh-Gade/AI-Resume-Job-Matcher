"""
Lambda function to generate resume optimization suggestions
"""
import json
import boto3
import os
from openai import OpenAI
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

RESUMES_TABLE = os.getenv('DYNAMODB_RESUMES_TABLE', 'ResumeMatcherResumes')
JOBS_TABLE = os.getenv('DYNAMODB_JOBS_TABLE', 'ResumeMatcherJobs')


def generate_optimization_suggestions(resume_data, job_data):
    """Use AI to generate resume optimization suggestions"""
    prompt = f"""
    You are a career coach helping a student optimize their resume for a specific job.
    
    Current Resume:
    - Skills: {', '.join(resume_data.get('skills', []))}
    - Experience: {json.dumps(resume_data.get('experience', []), indent=2)}
    - Education: {json.dumps(resume_data.get('education', []), indent=2)}
    - Projects: {', '.join(resume_data.get('projects', []))}
    
    Target Job:
    - Title: {job_data.get('title')}
    - Company: {job_data.get('company')}
    - Required Experience: {job_data.get('experience', 'Not specified')}
    
    Provide actionable suggestions to improve the resume for this job:
    1. Skills to add or highlight
    2. Keywords to include for ATS
    3. Experience descriptions to emphasize
    4. Projects to highlight
    5. Overall formatting tips
    
    Return as JSON:
    {{
        "missing_skills": ["skill1", "skill2"],
        "ats_keywords": ["keyword1", "keyword2"],
        "experience_tips": ["tip1", "tip2"],
        "project_suggestions": ["suggestion1"],
        "formatting_tips": ["tip1", "tip2"],
        "overall_score": 75,
        "priority_actions": ["action1", "action2"]
    }}
    
    Return only valid JSON, no additional text.
    """
    
    response = openai_client.chat.completions.create(
        model=os.getenv('OPENAI_MODEL', 'gpt-4o-mini'),
        messages=[
            {"role": "system", "content": "You are a career coach specializing in resume optimization for Indian students."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.5,
        max_tokens=800
    )
    
    result = response.choices[0].message.content
    if result.startswith("```json"):
        result = result[7:-3].strip()
    elif result.startswith("```"):
        result = result[3:-3].strip()
    
    return json.loads(result)


def lambda_handler(event, context):
    """
    Main Lambda handler for resume optimization
    
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
        
        # Generate suggestions
        suggestions = generate_optimization_suggestions(resume_data, job_data)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Optimization suggestions generated',
                'job_title': job_data.get('title'),
                'company': job_data.get('company'),
                'suggestions': suggestions
            })
        }
        
    except Exception as e:
        print(f"Error generating optimization suggestions: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
