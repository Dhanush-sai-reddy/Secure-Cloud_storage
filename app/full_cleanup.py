import os
import json
import boto3
from dotenv import load_dotenv

load_dotenv()

def cleanup():
    print("--- Starting Full Project Cleanup ---")

    # 1. Clear S3 Bucket
    bucket_name = os.getenv("S3_BUCKET_NAME")
    if bucket_name:
        try:
            s3 = boto3.resource('s3')
            bucket = s3.Bucket(bucket_name)
            print(f" Deleting all objects in S3 bucket: {bucket_name}...")
            bucket.objects.all().delete()
            print(" [+] S3 Bucket cleared.")
        except Exception as e:
            print(f" [!] S3 Cleanup Error: {e}")

    # 2. Clear Local Index files
    files_to_clear = ["cloud_index.json", "local_df.json"]
    for filename in files_to_clear:
        if os.path.exists(filename):
            with open(filename, "w") as f:
                json.dump({}, f)
            print(f" [+] {filename} reset to empty.")

    # 3. Clean local directories
    dirs_to_clean = ["temp_uploads", "downloads"]
    for directory in dirs_to_clean:
        if os.path.exists(directory):
            print(f" Cleaning {directory} directory...")
            for file in os.listdir(directory):
                file_path = os.path.join(directory, file)
                try:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                except Exception as e:
                    print(f"  [!] Could not delete {file}: {e}")
            print(f" [+] {directory} directory cleaned.")

    print("\n--- Cleanup Complete! Project is fresh and ready. ---")

if __name__ == "__main__":
    cleanup()
