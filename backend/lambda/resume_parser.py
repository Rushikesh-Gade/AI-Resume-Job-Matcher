"""
Lambda function to parse uploaded resumes and extract key information
"""
import json
import boto3
import os
from openai import OpenAI
from PyPDF2 import PdfReader
from docx import Document
import io

s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

RESUMES_TABLE = os.getenv('DYNAMODB_RESUMES_TABLE', 'ResumeMatcherResumes')
S3_BUCKET = os.getenv('S3_RESUME_BUCKET', 'resume-matcher-resumes')


def extract_text_from_pdf(file_content):
    """Extract text from PDF file"""
    pdf_file = io.BytesIO(file_content)
    pdf_reader = PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text


def extract_text_from_docx(file_content):
    """Extract text from DOCX file"""
    docx_file = io.BytesIO(file_content)
    doc = Document(docx_file)
    text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
    return text


def parse_resume_with_ai(resume_text):
    """Use OpenAI to extract structured data from resume text"""
    prompt = f"""
    Extract the following information from this resume and return it as JSON:
    
    {{
        "name": "Full name",
        "email": "Email address",
        "phone": "Phone number",
        "skills": ["skill1", "skill2", ...],
        "experience": [
            {{
                "company": "Company name",
                "role": "Job title",
                "duration": "Time period",
                "description": "Brief description"
            }}
        ],
        "education": [
            {{
                "degree": "Degree name",
                "institution": "College/University",
                "year": "Graduation year"
            }}
        ],
        "projects": ["project1", "project2", ...],
        "certifications": ["cert1", "cert2", ...]
    }}
    
    Resume text:
    {resume_text}
    
    Return only valid JSON, no additional text.
    """
    
    response = openai_client.chat.completions.create(
        model=os.getenv('OPENAI_MODEL', 'gpt-4o-mini'),
        messages=[
            {"role": "system", "content": "You are a resume parser that extracts structured data from resumes."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=1500
    )
    
    result = response.choices[0].message.content
    # Remove markdown code blocks if present
    if result.startswith("```json"):
        result = result[7:-3].strip()
    elif result.startswith("```"):
        result = result[3:-3].strip()
    
    return json.loads(result)


def lambda_handler(event, context):
    """
    Main Lambda handler for resume parsing
    
    Expected event format:
    {
        "user_id": "user123",
        "resume_key": "resumes/user123/resume.pdf"
    }
    """
    try:
        user_id = event['user_id']
        resume_key = event['resume_key']
        
        # Download resume from S3
        response = s3_client.get_object(Bucket=S3_BUCKET, Key=resume_key)
        file_content = response['Body'].read()
        
        # Extract text based on file type
        if resume_key.endswith('.pdf'):
            resume_text = extract_text_from_pdf(file_content)
        elif resume_key.endswith('.docx'):
            resume_text = extract_text_from_docx(file_content)
        else:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Unsupported file format'})
            }
        
        # Parse resume using AI
        parsed_data = parse_resume_with_ai(resume_text)
        
        # Store parsed data in DynamoDB
        table = dynamodb.Table(RESUMES_TABLE)
        table.put_item(
            Item={
                'user_id': user_id,
                'resume_key': resume_key,
                'parsed_data': parsed_data,
                'raw_text': resume_text[:5000],  # Store first 5000 chars
                'created_at': context.request_id
            }
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Resume parsed successfully',
                'data': parsed_data
            })
        }
        
    except Exception as e:
        print(f"Error parsing resume: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
