"""
S3 helper functions for file operations
"""
import boto3
import os
from datetime import datetime

s3_client = boto3.client('s3')


def upload_file_to_s3(file_content, bucket, key):
    """Upload file to S3 bucket"""
    try:
        s3_client.put_object(
            Bucket=bucket,
            Key=key,
            Body=file_content
        )
        return True, key
    except Exception as e:
        return False, str(e)


def download_file_from_s3(bucket, key):
    """Download file from S3 bucket"""
    try:
        response = s3_client.get_object(Bucket=bucket, Key=key)
        return response['Body'].read()
    except Exception as e:
        print(f"Error downloading file: {str(e)}")
        return None


def generate_presigned_url(bucket, key, expiration=3600):
    """Generate presigned URL for file access"""
    try:
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket, 'Key': key},
            ExpiresIn=expiration
        )
        return url
    except Exception as e:
        print(f"Error generating presigned URL: {str(e)}")
        return None


def delete_file_from_s3(bucket, key):
    """Delete file from S3 bucket"""
    try:
        s3_client.delete_object(Bucket=bucket, Key=key)
        return True
    except Exception as e:
        print(f"Error deleting file: {str(e)}")
        return False


def list_files_in_bucket(bucket, prefix=''):
    """List all files in S3 bucket with given prefix"""
    try:
        response = s3_client.list_objects_v2(
            Bucket=bucket,
            Prefix=prefix
        )
        
        if 'Contents' in response:
            return [obj['Key'] for obj in response['Contents']]
        return []
    except Exception as e:
        print(f"Error listing files: {str(e)}")
        return []
