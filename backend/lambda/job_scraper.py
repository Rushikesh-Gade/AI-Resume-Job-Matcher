"""
Lambda function to scrape job postings from multiple sources
"""
import json
import boto3
import requests
from bs4 import BeautifulSoup
import time
import hashlib
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
JOBS_TABLE = os.getenv('DYNAMODB_JOBS_TABLE', 'ResumeMatcherJobs')


def generate_job_id(title, company):
    """Generate unique job ID from title and company"""
    unique_string = f"{title}_{company}".lower()
    return hashlib.md5(unique_string.encode()).hexdigest()


def scrape_naukri(keywords="software engineer", location="India", max_jobs=50):
    """Scrape jobs from Naukri.com"""
    jobs = []
    
    try:
        # Note: This is a simplified example. Real implementation needs proper headers,
        # rate limiting, and handling of Naukri's anti-scraping measures
        url = f"https://www.naukri.com/{keywords.replace(' ', '-')}-jobs"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Parse job listings (selectors may need updates)
        job_cards = soup.find_all('article', class_='jobTuple', limit=max_jobs)
        
        for card in job_cards:
            try:
                title = card.find('a', class_='title').text.strip()
                company = card.find('a', class_='subTitle').text.strip()
                experience = card.find('span', class_='expwdth').text.strip() if card.find('span', class_='expwdth') else 'Not specified'
                location_elem = card.find('span', class_='locWdth')
                job_location = location_elem.text.strip() if location_elem else 'Not specified'
                
                jobs.append({
                    'job_id': generate_job_id(title, company),
                    'title': title,
                    'company': company,
                    'location': job_location,
                    'experience': experience,
                    'source': 'naukri',
                    'scraped_at': datetime.utcnow().isoformat()
                })
                
            except Exception as e:
                print(f"Error parsing job card: {str(e)}")
                continue
        
        time.sleep(2)  # Rate limiting
        
    except Exception as e:
        print(f"Error scraping Naukri: {str(e)}")
    
    return jobs


def scrape_linkedin(keywords="software engineer", max_jobs=50):
    """Scrape jobs from LinkedIn (placeholder - requires LinkedIn API or proper scraping)"""
    # Note: LinkedIn has strict anti-scraping measures
    # In production, use LinkedIn Jobs API or a service like ScraperAPI
    jobs = []
    
    print("LinkedIn scraping requires API access or specialized tools")
    # Placeholder implementation
    
    return jobs


def scrape_internshala(keywords="software", max_jobs=50):
    """Scrape jobs from Internshala"""
    jobs = []
    
    try:
        url = f"https://internshala.com/jobs/{keywords}-jobs/"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Parse job listings (selectors may need updates)
        job_cards = soup.find_all('div', class_='individual_internship', limit=max_jobs)
        
        for card in job_cards:
            try:
                title = card.find('h3', class_='job-internship-name').text.strip()
                company = card.find('p', class_='company-name').text.strip()
                location_elem = card.find('span', class_='location_link')
                job_location = location_elem.text.strip() if location_elem else 'Remote'
                
                jobs.append({
                    'job_id': generate_job_id(title, company),
                    'title': title,
                    'company': company,
                    'location': job_location,
                    'experience': '0-1 years',
                    'source': 'internshala',
                    'scraped_at': datetime.utcnow().isoformat()
                })
                
            except Exception as e:
                print(f"Error parsing job card: {str(e)}")
                continue
        
        time.sleep(2)  # Rate limiting
        
    except Exception as e:
        print(f"Error scraping Internshala: {str(e)}")
    
    return jobs


def store_jobs_in_dynamodb(jobs):
    """Store scraped jobs in DynamoDB"""
    table = dynamodb.Table(JOBS_TABLE)
    stored_count = 0
    
    for job in jobs:
        try:
            table.put_item(Item=job)
            stored_count += 1
        except Exception as e:
            print(f"Error storing job {job['job_id']}: {str(e)}")
    
    return stored_count


def lambda_handler(event, context):
    """
    Main Lambda handler for job scraping
    Triggered daily by EventBridge
    """
    try:
        all_jobs = []
        
        # Scrape from multiple sources
        print("Scraping Naukri...")
        naukri_jobs = scrape_naukri()
        all_jobs.extend(naukri_jobs)
        
        print("Scraping Internshala...")
        internshala_jobs = scrape_internshala()
        all_jobs.extend(internshala_jobs)
        
        # LinkedIn requires API access
        # linkedin_jobs = scrape_linkedin()
        # all_jobs.extend(linkedin_jobs)
        
        # Store in DynamoDB
        stored_count = store_jobs_in_dynamodb(all_jobs)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Job scraping completed',
                'total_jobs_scraped': len(all_jobs),
                'jobs_stored': stored_count,
                'sources': ['naukri', 'internshala']
            })
        }
        
    except Exception as e:
        print(f"Error in job scraper: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
