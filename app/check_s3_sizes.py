import boto3
import os
from dotenv import load_dotenv

load_dotenv()
BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

s3 = boto3.client('s3')
response = s3.list_objects_v2(Bucket=BUCKET_NAME)

if 'Contents' in response:
    for obj in response['Contents']:
        print(f"{obj['Key']}: {obj['Size']} bytes")
else:
    print("Bucket is empty.")
