"""
Lambda function to calculate match scores between resumes and jobs
"""
import json
import boto3
import os
from openai import OpenAI

dynamodb = boto3.resource('dynamodb')
openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

RESUMES_TABLE = os.getenv('DYNAMODB_RESUMES_TABLE', 'ResumeMatcherResumes')
JOBS_TABLE = os.getenv('DYNAMODB_JOBS_TABLE', 'ResumeMatcherJobs')
MATCHES_TABLE = os.getenv('DYNAMODB_MATCHES_TABLE', 'ResumeMatcherMatches')


def calculate_match_score(resume_data, job_data):
    """
    Use AI to calculate match score and generate explanation
    """
    prompt = f"""
    You are a job matching expert. Calculate how well this candidate matches the job requirements.
    
    Candidate Profile:
    - Skills: {', '.join(resume_data.get('skills', []))}
    - Experience: {len(resume_data.get('experience', []))} positions
    - Education: {resume_data.get('education', [])}
    
    Job Requirements:
    - Title: {job_data.get('title', 'Not specified')}
    - Company: {job_data.get('company', 'Not specified')}
    - Required Experience: {job_data.get('experience', 'Not specified')}
    - Location: {job_data.get('location', 'Not specified')}
    
    Provide:
    1. Match score (0-100)
    2. Brief explanation of why this score was given
    3. List of matching skills
    4. List of missing skills (if any)
    
    Return as JSON:
    {{
        "score": 85,
        "explanation": "Strong match because...",
        "matching_skills": ["Python", "AWS"],
        "missing_skills": ["Docker", "Kubernetes"]
    }}
    
    Return only valid JSON, no additional text.
    """
    
    try:
        response = openai_client.chat.completions.create(
            model=os.getenv('OPENAI_MODEL', 'gpt-4o-mini'),
            messages=[
                {"role": "system", "content": "You are a job matching expert that calculates compatibility scores."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=500
        )
        
        result = response.choices[0].message.content
        
        # Clean up response
        if result.startswith("```json"):
            result = result[7:-3].strip()
        elif result.startswith("```"):
            result = result[3:-3].strip()
        
        return json.loads(result)
        
    except Exception as e:
        print(f"Error calculating match score: {str(e)}")
        # Fallback to basic matching
        return {
            "score": 50,
            "explanation": "Basic match calculation (AI unavailable)",
            "matching_skills": [],
            "missing_skills": []
        }


def store_match(user_id, job_id, match_data):
    """Store match score in DynamoDB"""
    table = dynamodb.Table(MATCHES_TABLE)
    
    table.put_item(
        Item={
            'user_id': user_id,
            'job_id': job_id,
            'match_score': match_data['score'],
            'explanation': match_data['explanation'],
            'matching_skills': match_data['matching_skills'],
            'missing_skills': match_data['missing_skills'],
            'calculated_at': datetime.utcnow().isoformat()
        }
    )


def lambda_handler(event, context):
    """
    Main Lambda handler for match calculation
    
    Expected event format:
    {
        "user_id": "user123",
        "job_ids": ["job1", "job2", ...]  // Optional, if not provided, match against all jobs
    }
    """
    try:
        user_id = event['user_id']
        
        # Get user's resume data
        resumes_table = dynamodb.Table(RESUMES_TABLE)
        resume_response = resumes_table.get_item(Key={'user_id': user_id})
        
        if 'Item' not in resume_response:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Resume not found for user'})
            }
        
        resume_data = resume_response['Item']['parsed_data']
        
        # Get jobs to match against
        jobs_table = dynamodb.Table(JOBS_TABLE)
        
        if 'job_ids' in event:
            # Match against specific jobs
            job_ids = event['job_ids']
            jobs = []
            for job_id in job_ids:
                job_response = jobs_table.get_item(Key={'job_id': job_id})
                if 'Item' in job_response:
                    jobs.append(job_response['Item'])
        else:
            # Match against all jobs (scan - expensive, use with caution)
            jobs_response = jobs_table.scan(Limit=100)
            jobs = jobs_response['Items']
        
        # Calculate matches
        matches = []
        for job in jobs:
            match_data = calculate_match_score(resume_data, job)
            match_data['job_id'] = job['job_id']
            match_data['job_title'] = job.get('title', 'Unknown')
            match_data['company'] = job.get('company', 'Unknown')
            
            # Store match
            store_match(user_id, job['job_id'], match_data)
            
            matches.append(match_data)
        
        # Sort by score
        matches.sort(key=lambda x: x['score'], reverse=True)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Match calculation completed',
                'total_matches': len(matches),
                'top_matches': matches[:10]  # Return top 10
            })
        }
        
    except Exception as e:
        print(f"Error in match engine: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
