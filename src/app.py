import json
import os
import uuid
import boto3

s3 = boto3.client("s3")

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
    
    if "body" not in event or event["body"] is None:
        return _resp(400, {"error": "Missing request body"})

    try:
        body = json.loads(event["body"])
    except json.JSONDecodeError:
        return _resp(400, {"error": "Body must be valid JSON"})

    file_name = body.get("fileName", "file")
    content_type = body.get("contentType", "application/octet-stream")

    ext = ""
    if "." in file_name:
        ext = "." + file_name.split(".")[-1].strip().lower()

    object_key = f"{uuid.uuid4().hex}{ext}"

    upload_url = s3.generate_presigned_url(
        ClientMethod="put_object",
        Params={
            "Bucket": BUCKET_NAME,
            "Key": object_key,
            "ContentType": content_type,
        },
        ExpiresIn=UPLOAD_EXPIRES,
    )

    body = {"uploadURL": upload_url, "objectKey": object_key}

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
    path_params = event.get("pathParameters") or {}
    object_key = path_params.get("objectKey")

    if not object_key:
        return _resp(400, {"error": "Missing path parameter: objectKey"})

    if ".." in object_key:
        return _resp(400, {"error": "Invalid objectKey"})

    download_url = s3.generate_presigned_url(
        ClientMethod="get_object",
        Params={"Bucket": BUCKET_NAME, "Key": object_key},
        ExpiresIn=DOWNLOAD_EXPIRES,
    )

    # Redirect with Location header
    return {
        "statusCode": REDIRECT_STATUS,
        "headers": {"Location": download_url},
        "body": "",
    }