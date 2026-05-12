import boto3
import os
from dotenv import load_dotenv

load_dotenv()
bucket_name = os.getenv("S3_BUCKET_NAME")

try:
    s3 = boto3.client('s3')
    response = s3.list_objects_v2(Bucket=bucket_name, MaxKeys=1)
    print(f"SUCCESS: Connected to bucket '{bucket_name}'")
except Exception as e:
    print(f"FAILURE: Could not connect to AWS/S3. Error: {e}")
