# Serverless Signed URL File Gateway

A secure, serverless S3 bucket file management gateway project built with AWS SAM (Serverless Application Model) that will provide pre-signed S3 URLs for secure file operations such as uploads and downloads without exposing direct S3 access to clients.

## Main Features

- ✅ Secure file uploads using pre-signed URLs (5-minute expiration)
- ✅ Secure file downloads via redirect (1-hour expiration)
- ✅ No direct S3 access required from clients

## 📄 Additional Documentation

All the details about this project, including architecture, IaC and Python snippets, proof of functionality screenshots and additional resources, please refer to: 

**[Serverless Signed URL File Gateway](https://docs.google.com/document/d/1NSL0b5yCUq9liQ_58pMX2OpLwqArvI25nWt7gernsdY/edit?usp=sharing)**

## Project Structure

```
.
├── .  github/
│   └── workflows/
│       └── deploy.yaml        # GitHub Actions deployment workflow
├── src/
│   └── app.py                 # Lambda function handlers
├── template.yaml              # AWS SAM infrastructure template
└── README.md                  # This file
```

## Architecture

This application uses:  
- **AWS Lambda:** For creating methods to react to their respective HTTP API endpoint triggers, get their events' information (body in POST and the object key for GET) and process them as needed with the involvement of the boto3 library for S3 bucket access. 
- **Amazon S3:** For storing the project's files and download them if required; being only accessible via the presigned URLs
- **API Gateway:** For generating the HTTP API REST endpoints for the Lambda functions to use in the respective GET and POST methods.  
- **IAM:** For limiting the compute layer's access to S3

## Prerequisites

Before forking and deploying, ensure you have an AWS account counting with the following aspects:  

- An Account ID (showcased at the right top of the AWS Console website like this XXXX-XXXX-XXXX)
- An IAM role called "githubconnect", which will need the following minimal permissions to deploy the stack. 
    - AmazonAPIGatewayAdministrator
    - AmazonS3FullAccess
    - AWSCloudFormationFullAccess
    - AWSLambda_FullAccess
    - AWSLambdaSQSQueueExecutionRole
    - IAMFullAccess

## Fork + Deployment Steps (via GitHub Actions)

### 1. Fork the Repository

1. Navigate to https://github.com/NickyGon/Serverless-Signed-URL-File-Gateway
2. Click the **Fork** button in the top-right corner
3. Select your GitHub account as the destination, changing the name it will be referred to if necessary

### 2. Configure AWS OIDC with GitHub

#### Create the IAM OIDC Identity Provider (one-time setup)

In your AWS Console:  

1. Navigate to **IAM** → **Identity providers** → **Add provider**
2. Select **OpenID Connect**
3. Set the following:  
   - **Provider URL**:  `https://token.actions.githubusercontent.com`
   - **Audience**: `sts.amazonaws.com`
4. Click **Add provider**

#### Create or Verify the `githubconnect` IAM Role

1. Navigate to **IAM** → **Roles** → **Create role**
2. Select **Web identity** as the trusted entity type
3. Choose the identity provider you just created
4. For **Audience**, select `sts.amazonaws.com`
5. Click **Next**
6. Attach the following policies:
   - `AmazonAPIGatewayAdministrator`
   - `AmazonS3FullAccess`
   - `AWSCloudFormationFullAccess`
   - `AWSLambda_FullAccess`
   - `AWSLambdaSQSQueueExecutionRole`
   - `IAMFullAccess`
7. Name the role:   `githubconnect`
8. Click **Create role**

#### Update the Trust Relationship

After creating the role, edit its trust policy: 

1. Navigate to **IAM** → **Roles** → **githubconnect** → **Trust relationships** → **Edit trust policy**
2. Replace with the following (update `YOUR_GITHUB_USERNAME`):

```json
{
  "Version": "2012-10-17",
  "Statement":   [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::YOUR_ACCOUNT_ID:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token. actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
            "token.actions.githubusercontent.com:sub": [
                "repo:YOUR_GITHUB_USERNAME/*",
                "repo:YOUR_GITHUB_USERNAME/*"
            ]
        }
      }
    }
  ]
}
```

3. Click **Update policy**

### 3. Configure GitHub Repository Variables

In your forked repository:

1. Go to **Settings** → **Secrets and variables** → **Actions** → **Variables** tab
2. Click **New repository variable**
3. Add the following variable:
   - **Name**: `AWS_ACCOUNT_ID`
   - **Value**: Your AWS Account ID (12-digit number, e.g., `123456789012`)
4. Click **Add variable**

### 4. Deploy the Application

The deployment happens automatically via GitHub Actions:  

1. Navigate to the **Actions** tab in your forked repository
2. You should see the workflow "Deploy Serverless Signed URL File Gateway"
3. The workflow will automatically trigger on any push to the `main` branch

To trigger a deployment:  

```bash
# Make a small change (e.g., update README or code)
git add .
git commit -m "Trigger deployment"
git push origin main
```

Or manually trigger the workflow: 

1. Go to **Actions** tab
2. Select "Deploy Serverless Signed URL File Gateway"
3. Click **Run workflow** → **Run workflow**

### 5. Monitor the Deployment

1. Click on the running workflow in the **Actions** tab
2. Click on the **deploy** job to see real-time logs
3. The deployment typically takes 2-3 minutes

### 6. Get Your API Endpoints

After successful deployment, retrieve your endpoints: 
1. Navigate to **CloudFormation** → **Stacks**
2. Select the `url-file-gateway` stack
3. Click the **Outputs** tab
4. Note the following values:
   - **ApiBaseUrl**: Base URL for your API.  **KEEP IT FOR the "curl" and/or Postman tests**
   - **FilesPostEndpoint**: POST endpoint for upload URLs (mostly for referral)
   - **FilesGetEndpoint**: GET endpoint for downloads (mostly for referral)
   - **BucketName**: Your S3 bucket name

## ⚙️ Configuration

### Environment Variables

The Lambda functions use the following configurable environment variables (set in `template.yaml`):

#### PrepareS3UploadFunction
- `BUCKET_NAME`: S3 bucket for file storage (auto-configured)
- `UPLOAD_URL_EXPIRES_SECONDS`: Pre-signed upload URL expiration (default: `300` seconds / 5 minutes)

#### DownloadRedirectFunction
- `BUCKET_NAME`: S3 bucket for file storage (auto-configured)
- `DOWNLOAD_URL_EXPIRES_SECONDS`: Pre-signed download URL expiration (default: `3600` seconds / 1 hour)
- `REDIRECT_STATUS_CODE`: HTTP redirect status code (default: `302`)

### Customizing Expiration Times

Edit `template.yaml` to adjust expiration times:

```yaml
Environment:
  Variables:
    UPLOAD_URL_EXPIRES_SECONDS: "600"    # 10 minutes
    DOWNLOAD_URL_EXPIRES_SECONDS: "7200" # 2 hours
```

Then commit and push to trigger redeployment:  

```bash
git add template.yaml
git commit -m "Update expiration times"
git push origin main
```

## Testing with cURL (in CMS)

### 1. POST /files
#### A. Request a pre-signed URL with the desired file name and file type

```bash
curl -X POST https://YOUR_API_ID.execute-api.YOUR_REGION.amazonaws.com/prod/files \
  -H "Content-Type: application/json" \
  -d '{"fileName": "test-image.png", "contentType": "image/png"}'
```
(for CMS, the JSON request body requires to be written like this **-d "{\"fileName\": \"googlelogo.png\",\"contentType\":\"image/png\"}"** )

**Expected Response:**
```json
{
  "uploadURL": "https://redirect-ACCOUNT-REGION. s3.amazonaws.com/test-image.png?X-Amz-Algorithm=..  .",
  "objectKey": "test-image.png"
}
```

#### B. Upload a File with the pre-signed URL

Use the `uploadURL` from the previous response:

```bash
curl -X PUT "UPLOAD_URL_FROM_STEP_1" \
  -H "Content-Type: image/png" \
  --data-binary "@/path/to/your/test-image.png"
```

(for CMS, the data binary option requires to be written like this **--data-binary @"C:\path\to\your\test-image.png"** )


### 2. GET /files/{objectKey}
#### A. Request a pre-signed download URL with the object key

Use the `objectKey` from the POST curl command:

```bash
curl -i "https://YOUR_API_ID.execute-api.YOUR_REGION.amazonaws.com/prod/files/test-image.png"
```

**Expected Response:**
```http
HTTP/1.1 302 Found
Content-Type: application/json
Content-Length: 0
Connection:  keep-alive
Date: Thu, 08 Jan 2026 21:01:58 GMT
X-Amzn-Trace-Id: Root=1-69601b46-161d06f519a89ea35584495f;Parent=42c6006fe21a9a61;Sampled=0;Lineage=1:24c59c21: 0
x-amzn-RequestId:  80ad6e45-ea01-41df-9bdd-5710fb942777
x-amz-apigw-id: W4kzFGeqIAMEFMQ=
Location: https://redirect-913073094287-us-east-1.s3.amazonaws.com/googlelogo.png?AWSAccessKeyId=ASIA5JF3FX2H7URVHL5I&Signature=9ToT6gLG79BdJsO9FGnRxk3%2BgYo%3D&x-amz-security-token=... 
```

The pre-signed Location URL can be tested in a browser to get the file

#### B. Testing the Location URL

```bash
curl -i "https://redirect-913073094287-us-east-1.s3.amazonaws.com/googlelogo.png?AWSAccessKeyId=ASIA5JF3FX2H7URVHL5I&Signature=9ToT6gLG79BdJsO9FGnRxk3%2BgYo%3D&x-amz-security-token=..."
```

**For a valid URL**
```http
HTTP/1.1 200 OK
x-amz-id-2: h9FYqzsIAVUn3bnaFMvn975ihChOqpAZ4lvx+DA2pKzhQrFVC7x3agALrqKXZYku+U8syaljZAw=
x-amz-request-id: 2BQ9NVK9KZAK2M4P
Date: Thu, 08 Jan 2026 21:38:31 GMT
Last-Modified: Thu, 08 Jan 2026 20:46:11 GMT
ETag:  "d35c7a1b40f2718c1a20ce38491cb006"
x-amz-server-side-encryption: AES256
Accept-Ranges: bytes
Content-Type: image/png
Content-Length: 2878
Server: AmazonS3
```

**For an expired URL**
```http
HTTP/1.1 403 Forbidden
x-amz-request-id: B15ZM9ZA3PCJ8SEJ
x-amz-id-2: T4goqQRvS54PxialZWS/J+Y7Z9GIbZMrmwJz7kNyS17Or+dOwvZpi6b4GDbdaAaqR94cjCmRZmPiskcmbuL2R42ZMe/7/cAu
Content-Type: application/xml
Transfer-Encoding: chunked
Date: Thu, 08 Jan 2026 22:18:34 GMT
Server: AmazonS3

<?xml version="1.0" encoding="UTF-8"?>
<Error><Code>AccessDenied</Code><Message>Request has expired</Message><Expires>2026-01-08T21:56:24Z</Expires><ServerTime>2026-01-08T22:18:36Z</ServerTime><RequestId>B15ZM9ZA3PCJ8SEJ</RequestId><HostId>>T4goqQRvS54PxialZWS/J+Y7Z9GIbZMrmwJz7kNyS17Or+dOwvZpi6b4GDbdaAaqR94cjCmRZmPiskcmbuL2R42ZMe/7/cAu</HostId></Error>
```

#### C.  Downloading the file with an automatic 302 redirection from the GET request

```bash
curl -L -v -o testimages.png "https://YOUR_API_ID.execute-api.YOUR_REGION.amazonaws. com/prod/files/test-image.png"
```

**Expected Response**
```bash
% Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
  0     0    0     0    0     0      0      0 --:--:-- --:--:-- --:--:--     0* Could not resolve host: yski688vgd.execute-api.us-east-1.amazonaws.com
* Store negative name resolve for yski688vgd.execute-api.us-east-1.amazonaws.com:443
* shutting down connection #0
curl: (6) Could not resolve host: yski688vgd.execute-api.us-east-1.amazonaws.com

C:\Users\nicol>curl -L -v -o googlelogo.png "https://ak0pjjvvei.execute-api.us-east-1.amazonaws.com/prod/files/googlelogo.png"
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
  0     0    0     0    0     0      0      0 --:--:-- --:--:-- --:--: --     0* Host ak0pjjvvei. execute-api.us-east-1.amazonaws.com:443 was resolved. 
* IPv6:  (none)
* IPv4: 3.164.28.30, 3.164.28.5, 3.164.28.83, 3.164.28.120
*   Trying 3.164.28.30:443...
* schannel: disabled automatic use of client certificate
* ALPN: curl offers http/1.1
* ALPN: server accepted http/1.1
* Established connection to ak0pjjvvei. execute-api.us-east-1.amazonaws.com (3.164.28.30 port 443) from 192.168.0.57 port 50463
* using HTTP/1.x
> GET /prod/files/googlelogo.png HTTP/1.1
> Host: ak0pjjvvei.execute-api.us-east-1.amazonaws.com
> User-Agent: curl/8.16.0
> Accept: */*
>
* Request completely sent off
* schannel: remote party requests renegotiation
* schannel: renegotiating SSL/TLS connection
* schannel: SSL/TLS connection renegotiated
< HTTP/1.1 302 Found
< Content-Type: application/json
< Content-Length: 0
< Connection: keep-alive
< Date: Thu, 08 Jan 2026 23:35:57 GMT
< X-Amzn-Trace-Id:  Root=1-69603f5c-367d2c4c5ccd74463e0010b2;Parent=1d5d055891f98713;Sampled=0;Lineage=1:24c59c21:0
< x-amzn-RequestId: 698f4d41-0ace-44e8-ac86-2be341734924
< x-amz-apigw-id: W47WgHvsIAMEtBQ=
< Location: https://redirect-913073094287-us-east-1.s3.amazonaws.com/googlelogo.png?AWSAccessKeyId=ASIA5JF3FX2H34MC2MXI&Signature=%2B5BGa3j2tj%2B98cSrLWK%2FsVXB%2BIk%3D&x-amz-security-token=IQoJb3JpZ2luX2VjEND%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLWVhc3QtMSJHMEUCIQDX6NVaeX1ZIn9uR2tJLuix1m9DQ7H4TF8BDhL5U1iBlAIgIZjMgflf2ttd5QwGPbJmtUPsEB6qvZLoXAXhoQbGINAqjQMImf%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FARAAGgw5MTMwNzMwOTQyODciDFoSwgVR%2FPBGVzfetirhAvM%2BTDFnpbc5XzBbv8SS5HEOOdLOIR%2BeFAeJ8FPDmklB8Sa7Qlct7M5pdwaokdKvfE6u3VCyGWRQFXFE%2F0OagPv4M%2FsjVZyB42igYC9WYLWtm65ihqDkD%2BeH7iKBNd57q1BbBCYRxxyNIz%2BDqtgUmvB3fgkTXUu0FmXddDoQz4DWnwUrBzs6ScH3M2hRo9ccSsDvxYLi7jk97QpF57CLdXtL4gU%2B6uiiIpsbIkpRHa6iaaol%2Bdhe%2BKGc0%2B5TdmpkSHZyKlvWsER8lFO8CSjqpvqQ63srfBBSGqsEp9ymCMnOPqgYoRWdUr%2BbIeQbLAqhBYMTMgdohRmfDdjpJTZM%2BAb2VZKjciYTW5avjdLVT1mWsT7P%2F73P8Q5RzyCD0Sh9B%2FtHaQ%2BdGeBC0P%2FMQs%2Fq90srgIcONhAI0MxG4BsM9FQwtHfO4Jr1OVEg%2FMqB53n2ekmbAg9A4FesuotArwZ243X1MNz%2BgMsGOp4Bp%2B%2FYZ9usb3y1xtmgdzJG%2F4wTvdfRBLJahwpPRuVD7%2BrxDU1D8tEOY93m5MPQCiW4OiJeUUMgN0u1IL3pcqJ%2F%2FVL0rn%2B5rDHaXvYPFCXaoUZHwGaHEH5Q1Aj4tcWwerBFuIT2O1yvzO1Jz668gPkkZYjk2teP9qcofwoyqVJnaGTnHXTnXLFGfV00Z4CAI4aThYVI2%2FZNMZqTmiIGB5o%3D&Expires=1767918957
< X-Cache:  Miss from cloudfront
< Via: 1.1 0d2303aa8a99228e662a12ce528c15c6.cloudfront.net (CloudFront)
< X-Amz-Cf-Pop: GRU3-P7
< X-Amz-Cf-Id: LtXBvJto5RHphJgK3Z4DQtaExGgHG_uevwfE7C9UkiW-96ZzUVLbhg==
* Ignoring the response-body
* setting size while ignoring
<
  0     0    0     0    0     0      0      0 --:--:--  0:00:01 --:--:--     0
* Connection #0 to host ak0pjjvvei.execute-api.us-east-1.amazonaws.com:443 left intact
* Issue another request to this URL:  'https://redirect-913073094287-us-east-1.s3.amazonaws.com/googlelogo. png?AWSAccessKeyId=ASIA5JF3FX2H34MC2MXI&Signature=%2B5BGa3j2tj%2B98cSrLWK%2FsVXB%2BIk%3D&x-amz-security-token=IQoJb3JpZ2luX2VjEND%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLWVhc3QtMSJHMEUCIQDX6NVaeX1ZIn9uR2tJLuix1m9DQ7H4TF8BDhL5U1iBlAIgIZjMgflf2ttd5QwGPbJmtUPsEB6qvZLoXAXhoQbGINAqjQMImf%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FARAAGgw5MTMwNzMwOTQyODciDFoSwgVR%2FPBGVzfetirhAvM%2BTDFnpbc5XzBbv8SS5HEOOdLOIR%2BeFAeJ8FPDmklB8Sa7Qlct7M5pdwaokdKvfE6u3VCyGWRQFXFE%2F0OagPv4M%2FsjVZyB42igYC9WYLWtm65ihqDkD%2BeH7iKBNd57q1BbBCYRxxyNIz%2BDqtgUmvB3fgkTXUu0FmXddDoQz4DWnwUrBzs6ScH3M2hRo9ccSsDvxYLi7jk97QpF57CLdXtL4gU%2B6uiiIpsbIkpRHa6iaaol%2Bdhe%2BKGc0%2B5TdmpkSHZyKlvWsER8lFO8CSjqpvqQ63srfBBSGqsEp9ymCMnOPqgYoRWdUr%2BbIeQbLAqhBYMTMgdohRmfDdjpJTZM%2BAb2VZKjciYTW5avjdLVT1mWsT7P%2F73P8Q5RzyCD0Sh9B%2FtHaQ%2BdGeBC0P%2FMQs%2Fq90srgIcONhAI0MxG4BsM9FQwtHfO4Jr1OVEg%2FMqB53n2ekmbAg9A4FesuotArwZ243X1MNz%2BgMsGOp4Bp%2B%2FYZ9usb3y1xtmgdzJG%2F4wTvdfRBLJahwpPRuVD7%2BrxDU1D8tEOY93m5MPQCiW4OiJeUUMgN0u1IL3pcqJ%2F%2FVL0rn%2B5rDHaXvYPFCXaoUZHwGaHEH5Q1Aj4tcWwerBFuIT2O1yvzO1Jz668gPkkZYjk2teP9qcofwoyqVJnaGTnHXTnXLFGfV00Z4CAI4aThYVI2%2FZNMZqTmiIGB5o%3D&Expires=1767918957'
* Host redirect-913073094287-us-east-1.s3.amazonaws.com:443 was resolved.
* IPv6: (none)
* IPv4: 16.15.202.79, 3.5.25.107, 16.182.100.89, 52.216.77.180, 52.217.225.73, 3.5.25.230, 54.231.202.177, 16.15.217.111
*   Trying 16.15.202.79:443...
* schannel: disabled automatic use of client certificate
* ALPN:  curl offers http/1.1
  0     0    0     0    0     0      0      0 --:--:--  0:00:01 --:--:--     0* ALPN: server accepted http/1.1
* Established connection to redirect-913073094287-us-east-1.s3.amazonaws.com (16.15.202.79 port 443) from 192.168.0.57 port 50466
* using HTTP/1.x
> GET /googlelogo.png? AWSAccessKeyId=ASIA5JF3FX2H34MC2MXI&Signature=%2B5BGa3j2tj%2B98cSrLWK%2FsVXB%2BIk%3D&x-amz-security-token=IQoJb3JpZ2luX2VjEND%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLWVhc3QtMSJHMEUCIQDX6NVaeX1ZIn9uR2tJLuix1m9DQ7H4TF8BDhL5U1iBlAIgIZjMgflf2ttd5QwGPbJmtUPsEB6qvZLoXAXhoQbGINAqjQMImf%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FARAAGgw5MTMwNzMwOTQyODciDFoSwgVR%2FPBGVzfetirhAvM%2BTDFnpbc5XzBbv8SS5HEOOdLOIR%2BeFAeJ8FPDmklB8Sa7Qlct7M5pdwaokdKvfE6u3VCyGWRQFXFE%2F0OagPv4M%2FsjVZyB42igYC9WYLWtm65ihqDkD%2BeH7iKBNd57q1BbBCYRxxyNIz%2BDqtgUmvB3fgkTXUu0FmXddDoQz4DWnwUrBzs6ScH3M2hRo9ccSsDvxYLi7jk97QpF57CLdXtL4gU%2B6uiiIpsbIkpRHa6iaaol%2Bdhe%2BKGc0%2B5TdmpkSHZyKlvWsER8lFO8CSjqpvqQ63srfBBSGqsEp9ymCMnOPqgYoRWdUr%2BbIeQbLAqhBYMTMgdohRmfDdjpJTZM%2BAb2VZKjciYTW5avjdLVT1mWsT7P%2F73P8Q5RzyCD0Sh9B%2FtHaQ%2BdGeBC0P%2FMQs%2Fq90srgIcONhAI0MxG4BsM9FQwtHfO4Jr1OVEg%2FMqB53n2ekmbAg9A4FesuotArwZ243X1MNz%2BgMsGOp4Bp%2B%2FYZ9usb3y1xtmgdzJG%2F4wTvdfRBLJahwpPRuVD7%2BrxDU1D8tEOY93m5MPQCiW4OiJeUUMgN0u1IL3pcqJ%2F%2FVL0rn%2B5rDHaXvYPFCXaoUZHwGaHEH5Q1Aj4tcWwerBFuIT2O1yvzO1Jz668gPkkZYjk2teP9qcofwoyqVJnaGTnHXTnXLFGfV00Z4CAI4aThYVI2%2FZNMZqTmiIGB5o%3D&Expires=1767918957 HTTP/1.1
> Host: redirect-913073094287-us-east-1.s3.amazonaws.com
> User-Agent: curl/8.16.0
> Accept: */*
>
* Request completely sent off
< HTTP/1.1 200 OK
< x-amz-id-2: EGYAveRLEnUtOJfW1abMdVaFglURUmEOPtchwPI5ZhGkpvLOKZrgvZOt00heRI0gaXO9nQAF+6HeXIj14w2KDLIvAHEuR/s3
< x-amz-request-id: WD79ASPTHTYNF1FG
< Date: Thu, 08 Jan 2026 23:35:58 GMT
< Last-Modified: Thu, 08 Jan 2026 20:46:11 GMT
< ETag: "d35c7a1b40f2718c1a20ce38491cb006"
< x-amz-server-side-encryption: AES256
< Accept-Ranges: bytes
< Content-Type: image/png
< Content-Length: 2878
< Server: AmazonS3
<
{ [2878 bytes data]
100  2878  100  2878    0     0   1402      0  0:00:02  0:00:02 --:--:--  5970
* Connection #1 to host redirect-913073094287-us-east-1.s3.amazonaws.com:443 left intact
```
