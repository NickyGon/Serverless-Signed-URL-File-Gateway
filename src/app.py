import json # For JSON handling
import os # For environment variables
import boto3 # For S3 interactions

s3 = boto3.client("s3")

# Variables to use from environment
BUCKET_NAME = os.environ["BUCKET_NAME"]
UPLOAD_EXPIRES = int(os.environ.get("UPLOAD_URL_EXPIRES_SECONDS", "300"))
DOWNLOAD_EXPIRES = int(os.environ.get("DOWNLOAD_URL_EXPIRES_SECONDS", "3600"))
REDIRECT_STATUS = int(os.environ.get("REDIRECT_STATUS_CODE", "302"))


def create_upload_url_handler(event, context):
    """
    POST /files
    Body:
      {"fileName": "photo.png", "contentType": "image/png"}
    Response:
      {"uploadURL": "...", "objectKey": "..."}
    """
    
    # Parsing the body for obtaining the filename and the file type
    # Should be a valid JSON structure
    if "body" not in event or event["body"] is None:
        return _resp(400, {"error": "Missing request body"})

    try:
        body = json.loads(event["body"])
    except json.JSONDecodeError:
        return _resp(400, {"error": "Body must be valid JSON"})

    file_name = body.get("fileName", "file")
    content_type = body.get("contentType", "application/octet-stream")

    # Generating the presigned URL for uploading the file with the S3 client's function aiming to the created bucket
    upload_url = s3.generate_presigned_url(
        ClientMethod="put_object",
        Params={
            "Bucket": BUCKET_NAME,
            "Key": file_name,
            "ContentType": content_type,
        },
        ExpiresIn=UPLOAD_EXPIRES,
    )

    # Returning the upload URL and the object key in the response body
    body = {"uploadURL": upload_url, "objectKey": file_name}

    return{
        "statusCode": 201,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps(body)
    }

def download_redirect_handler(event, context):
    """
    GET /files/{objectKey}
    Redirects to a signed GET URL (1 hour).
    """
    
    # Obtaining the objectKey from the path parameters. Launches an error if it's not found
    path_params = event.get("pathParameters") or {}
    object_key = path_params.get("objectKey")

    if not object_key:
        return _resp(400, {"error": "Missing path parameter: objectKey"})

    if ".." in object_key:
        return _resp(400, {"error": "Invalid objectKey"})

    # Generating the presigned URL for downloading the file with the S3 client's function aiming to the created bucket
    download_url = s3.generate_presigned_url(
        ClientMethod="get_object",
        Params={"Bucket": BUCKET_NAME, "Key": object_key},
        ExpiresIn=DOWNLOAD_EXPIRES,
    )

    # Returning a redirect GET response with the Location header containing the generated download URL
    return {
        "statusCode": REDIRECT_STATUS,
        "headers": {"Location": download_url},
        "body": "",
    }