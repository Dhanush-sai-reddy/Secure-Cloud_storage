# 🛡️ Secure Cloud Storage V2 - Setup Guide

This guide provides step-by-step instructions for setting up and running the Secure Cloud Storage (SCS) project after cloning.

## 📋 Prerequisites
- **Python 3.8+**
- **AWS Account**: Access to an S3 bucket.
- **AWS CLI Configured**: Or access keys ready.

---

## 🚀 Step 1: Environment Setup

1. **Clone the repository** and navigate to the `version2/app` directory.
2. **Install Dependencies**:
   ```bash
   pip install flask boto3 cryptography python-dotenv requests PyPDF2
   ```
3. **Configure Environment Variables**:
   Create a `.env` file in the `app/` directory with the following content:
   ```env
   AWS_ACCESS_KEY_ID=your_access_key
   AWS_SECRET_ACCESS_KEY=your_secret_key
   S3_BUCKET_NAME=your_bucket_name
   AWS_REGION=us-east-1
   # Use 127.0.0.1 for local testing, or your EC2 IP for production
   EC2_HOSTNAME=127.0.0.1 
   ```

---

## 🛠️ Step 2: Start the Index Server (Hexie)

The system requires an index server to manage the encrypted keyword chain.

### Option A: Local Testing (Recommended)
Run the local mock server to simulate the EC2 index service:
```bash
python local_server.py
```
*Keep this terminal open.*

### Option B: Production (AWS EC2)
If deploying to EC2, ensure the `server.py` on your instance is updated to support the `f_hash` field (Jianding verification).
1. SSH into your EC2.
2. Run the server: `python3 server.py`.

---

## 🌐 Step 3: Run the Main Application

Open a new terminal and run:
```bash
python app.py
```
Access the application at: **http://127.0.0.1:5030**

---

## 💡 Usage Tips & Troubleshooting

### 1. Keyword Extraction
- The system extracts keywords from filenames and file content (PDF/TXT).
- **Alphanumeric support**: Words like `test123` are supported.
- Keywords must be at least **3 characters** long.

### 2. Jianding Verification
- Every retrieval includes a cryptographic integrity check. If a file is tampered with in S3, the system will block the download and alert you.

### 3. Browser Cache (CRITICAL)
- If you make changes to the Javascript logic and don't see them, perform a **Hard Refresh**:
  - Windows: `Ctrl + F5`
  - Mac: `Cmd + Shift + R`

### 4. Cleanup
To wipe your S3 bucket and reset the local index for a fresh start, use the included cleanup utility:
```bash
python full_cleanup.py
```

---

## 🛡️ Security Note
The `MASTER_KEY` in `encryption.py` is currently set to a testing value. For production use, this should be moved to an environment variable or a Key Management Service (KMS).
