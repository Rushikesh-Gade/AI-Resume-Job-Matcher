# AI-Powered Resume-Job Matcher

A cloud-based platform that helps students find the best-matching jobs by analyzing their resume against available job postings using AI.

## Overview

This system scrapes job listings from multiple Indian job portals (Naukri, LinkedIn, Internshala), scores each match using AI, and provides personalized recommendations with resume optimization suggestions.

## Features

- 📄 **Resume Analysis** - Upload your resume and get automatic skill extraction
- 🔍 **Smart Job Matching** - AI-powered matching with 0-100% compatibility scores
- 📊 **Match Explanations** - Understand why each job is a good or bad fit
- ✍️ **Resume Optimization** - Get personalized suggestions to improve your resume
- 📝 **Cover Letter Generation** - Auto-generate tailored cover letters for each job
- 📈 **Application Tracking** - Track your applications and success rates
- 📧 **Email Notifications** - Get alerts for high-match jobs (70%+)

## Tech Stack

### Cloud Services (AWS)
- **Lambda** - Serverless functions for backend logic
- **S3** - Resume and document storage
- **DynamoDB** - User profiles and job data
- **API Gateway** - REST API endpoints
- **EventBridge** - Daily job scraping scheduler
- **SES** - Email notifications

### AI/ML
- **OpenAI API** - Resume parsing, match scoring, optimization suggestions

### Backend
- **Python 3.12** - Lambda functions
- **BeautifulSoup4** - Web scraping
- **boto3** - AWS SDK

### Frontend
- **React** - User interface
- **Axios** - API calls

## Budget

- AWS Services: $0-2/month (free tier)
- OpenAI API: $5-8/month
- **Total: Under $10/month**

## Project Status

🚧 **In Development** - Requirements phase completed

## Getting Started

Coming soon...

## License

MIT License

## Author

Rushikesh Gade
