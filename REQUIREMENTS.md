# Requirements Document

## Introduction

The AI-Powered Resume-Job Matcher is a cloud-based platform designed to help Indian students optimize their job search during campus placements. The system analyzes student resumes, scrapes job postings from Indian job portals, uses AI to calculate match scores, and provides personalized recommendations for resume improvements and cover letter generation.

## Target Users

- Indian college students preparing for campus placements
- Early-career professionals (0-2 years experience)
- Job seekers looking for entry-level positions

## Core Features

### 1. Resume Upload and Analysis
- Support PDF and DOCX formats (max 5MB)
- Extract skills, experience, education automatically
- Store securely in AWS S3
- Allow multiple resume versions

### 2. Job Scraping
- Daily scraping from Naukri.com, LinkedIn India, Internshala
- Extract job title, company, location, skills, experience level
- Deduplicate job postings
- Store in DynamoDB

### 3. AI-Powered Matching
- Calculate 0-100% match score for each job
- Compare skills, experience, education requirements
- Generate detailed match explanations
- Rank jobs by compatibility

### 4. Resume Optimization
- Identify missing skills for specific jobs
- Suggest resume improvements
- Recommend ATS-friendly keywords
- Highlight relevant experience

### 5. Cover Letter Generation
- Auto-generate personalized cover letters (250-400 words)
- Reference specific job requirements
- Professional tone for Indian job market
- Store in S3

### 6. Application Tracking
- Track application status (Applied, Interview, Rejected, Offer)
- Calculate response rates
- Analyze success patterns
- Compare match scores vs outcomes

### 7. Notifications
- Email alerts for 70%+ matches
- Daily job digest
- Configurable preferences

## Technical Requirements

### AWS Services (Free Tier)
- Lambda (Python 3.12)
- S3 (resume storage)
- DynamoDB (data storage)
- API Gateway (REST API)
- EventBridge (daily scheduler)
- SES (email notifications)

### AI Integration
- OpenAI API (GPT-4o-mini)
- Budget: $5-8/month

### Performance
- Resume parsing: < 30 seconds
- Match scoring: < 5 seconds per job
- API response: < 2 seconds
- Support 100+ concurrent users

### Security
- Password hashing
- Session tokens (24-hour expiry)
- User data isolation
- Secure file storage

## Budget Constraints

- Total: $10/month maximum
- AWS: $0-2/month (free tier)
- OpenAI: $5-8/month
- Cost monitoring and alerts

## Success Metrics

- Scrape 100+ jobs daily
- 90%+ resume parsing accuracy
- Generate match scores in < 5 seconds
- Stay within budget
- Support 10-20 demo users

## Out of Scope (MVP)

- Real-time push notifications
- Video resume analysis
- Interview scheduling
- Salary comparison
- Company reviews
- Mobile app
- Multi-language support

## Timeline

5-6 weeks to MVP completion
