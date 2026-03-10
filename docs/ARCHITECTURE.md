# System Architecture

## Overview

The AI-Powered Resume-Job Matcher follows a serverless architecture using AWS services to minimize costs while maintaining scalability.

## Architecture Diagram

```
┌─────────────┐
│   Student   │
│  (Browser)  │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│  React Frontend │
│   (S3 + CF)     │
└────────┬────────┘
         │
         ▼
┌──────────────────┐
│   API Gateway    │
│   (REST API)     │
└────────┬─────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐ ┌────────────┐
│ Lambda │ │  DynamoDB  │
│Functions│ │  (NoSQL)   │
└───┬────┘ └────────────┘
    │
    ├─► Resume Parser
    ├─► Job Scraper
    ├─► Match Engine
    ├─► Resume Optimizer
    └─► Cover Letter Gen
         │
         ▼
    ┌──────────┐
    │ OpenAI   │
    │   API    │
    └──────────┘
         │
         ▼
    ┌──────────┐
    │    S3    │
    │ (Storage)│
    └──────────┘
         │
         ▼
    ┌──────────┐
    │   SES    │
    │ (Email)  │
    └──────────┘
```

## Components

### 1. Frontend Layer
- **Technology**: React.js
- **Hosting**: AWS S3 + CloudFront (optional)
- **Purpose**: User interface for resume upload, job browsing, application tracking

### 2. API Layer
- **Service**: AWS API Gateway
- **Type**: REST API
- **Authentication**: JWT tokens
- **Endpoints**:
  - POST /resume/upload
  - GET /jobs/matches
  - POST /resume/optimize
  - POST /coverletter/generate
  - GET /applications
  - PUT /applications/{id}

### 3. Compute Layer
- **Service**: AWS Lambda
- **Runtime**: Python 3.12
- **Functions**:
  - `resume-parser`: Extract data from uploaded resumes
  - `job-scraper`: Scrape jobs from portals
  - `match-engine`: Calculate compatibility scores
  - `resume-optimizer`: Generate improvement suggestions
  - `coverletter-generator`: Create tailored cover letters
  - `notification-sender`: Send email alerts

### 4. Data Layer
- **Service**: AWS DynamoDB
- **Tables**:
  - `Users`: User profiles and authentication
  - `Resumes`: Parsed resume data
  - `Jobs`: Scraped job postings
  - `Matches`: Match scores and explanations
  - `Applications`: Application tracking data

### 5. Storage Layer
- **Service**: AWS S3
- **Buckets**:
  - `resumes-bucket`: Original resume files
  - `coverletters-bucket`: Generated cover letters
  - `frontend-bucket`: React app hosting

### 6. Scheduler Layer
- **Service**: AWS EventBridge
- **Schedule**: Daily at 6:00 AM IST
- **Triggers**: Job scraper Lambda function

### 7. Notification Layer
- **Service**: AWS SES
- **Purpose**: Send email notifications for high-match jobs

### 8. AI Layer
- **Service**: OpenAI API
- **Model**: GPT-4o-mini
- **Usage**:
  - Resume parsing and skill extraction
  - Match score calculation and explanation
  - Resume optimization suggestions
  - Cover letter generation

## Data Flow

### Resume Upload Flow
1. User uploads resume via React frontend
2. Frontend calls API Gateway POST /resume/upload
3. API Gateway triggers `resume-parser` Lambda
4. Lambda stores file in S3
5. Lambda calls OpenAI API to extract skills/experience
6. Lambda stores parsed data in DynamoDB
7. Lambda returns success response

### Job Matching Flow
1. EventBridge triggers `job-scraper` Lambda daily
2. Lambda scrapes Naukri, LinkedIn, Internshala
3. Lambda stores jobs in DynamoDB
4. Lambda triggers `match-engine` for all users
5. Match engine calculates scores using OpenAI
6. Scores stored in DynamoDB
7. If score > 70%, `notification-sender` sends email via SES

### Resume Optimization Flow
1. User requests optimization for specific job
2. Frontend calls API Gateway POST /resume/optimize
3. API Gateway triggers `resume-optimizer` Lambda
4. Lambda retrieves user profile and job details from DynamoDB
5. Lambda calls OpenAI API for suggestions
6. Lambda returns optimization tips

## Security

### Authentication
- JWT tokens with 24-hour expiry
- Password hashing using bcrypt
- Session management in DynamoDB

### Authorization
- User data isolation (users can only access their own data)
- S3 bucket policies restrict file access
- Lambda execution roles with least privilege

### Data Protection
- HTTPS for all API calls
- Encrypted S3 storage
- DynamoDB encryption at rest

## Scalability

### Current Capacity
- 100+ concurrent users
- 500+ jobs scraped daily
- 50 match calculations per minute

### Auto-Scaling
- Lambda: Automatic scaling (up to 1000 concurrent executions)
- DynamoDB: On-demand capacity mode
- API Gateway: Handles 10,000 requests per second

## Cost Optimization

### Free Tier Usage
- Lambda: 1M requests/month free
- DynamoDB: 25GB storage free
- S3: 5GB storage free
- API Gateway: 1M requests/month free
- SES: 62,000 emails/month free (from EC2)

### Paid Services
- OpenAI API: ~$5-8/month
- Total: < $10/month

## Monitoring

### CloudWatch Metrics
- Lambda execution time and errors
- API Gateway request count and latency
- DynamoDB read/write capacity
- S3 storage usage

### Logging
- Lambda function logs
- API Gateway access logs
- Error tracking and alerting

## Disaster Recovery

### Backup Strategy
- DynamoDB: Point-in-time recovery enabled
- S3: Versioning enabled for resume bucket
- Regular exports to backup bucket

### Recovery Time
- RTO: < 1 hour
- RPO: < 24 hours
