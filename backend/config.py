"""
Configuration settings for the AI Resume Job Matcher
"""
import os

# AWS Configuration
AWS_REGION = os.getenv('AWS_REGION', 'ap-south-1')
S3_RESUME_BUCKET = os.getenv('S3_RESUME_BUCKET', 'resume-matcher-resumes')
S3_COVERLETTER_BUCKET = os.getenv('S3_COVERLETTER_BUCKET', 'resume-matcher-coverletters')

# DynamoDB Tables
DYNAMODB_USERS_TABLE = os.getenv('DYNAMODB_USERS_TABLE', 'ResumeMatcherUsers')
DYNAMODB_RESUMES_TABLE = os.getenv('DYNAMODB_RESUMES_TABLE', 'ResumeMatcherResumes')
DYNAMODB_JOBS_TABLE = os.getenv('DYNAMODB_JOBS_TABLE', 'ResumeMatcherJobs')
DYNAMODB_MATCHES_TABLE = os.getenv('DYNAMODB_MATCHES_TABLE', 'ResumeMatcherMatches')
DYNAMODB_APPLICATIONS_TABLE = os.getenv('DYNAMODB_APPLICATIONS_TABLE', 'ResumeMatcherApplications')

# OpenAI Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
OPENAI_MAX_TOKENS = int(os.getenv('OPENAI_MAX_TOKENS', '1000'))

# Job Scraping Configuration
JOB_SOURCES = ['naukri', 'linkedin', 'internshala']
SCRAPING_DELAY = int(os.getenv('SCRAPING_DELAY', '2'))  # seconds between requests
MAX_JOBS_PER_SOURCE = int(os.getenv('MAX_JOBS_PER_SOURCE', '200'))

# Matching Configuration
MIN_MATCH_SCORE = int(os.getenv('MIN_MATCH_SCORE', '50'))
HIGH_MATCH_THRESHOLD = int(os.getenv('HIGH_MATCH_THRESHOLD', '70'))

# Email Configuration
SES_SENDER_EMAIL = os.getenv('SES_SENDER_EMAIL', 'noreply@resumematcher.com')
SES_REGION = os.getenv('SES_REGION', 'ap-south-1')

# Security Configuration
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24

# File Upload Configuration
MAX_RESUME_SIZE_MB = 5
ALLOWED_RESUME_EXTENSIONS = ['.pdf', '.docx']

# Performance Configuration
LAMBDA_TIMEOUT_SECONDS = 300
BATCH_SIZE = 50
