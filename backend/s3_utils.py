import boto3
import os
from botocore.exceptions import NoCredentialsError

s3_client = boto3.client(
    's3',
    endpoint_url=os.getenv("S3_ENDPOINT"),
    aws_access_key_id=os.getenv("S3_ACCESS_KEY"),
    aws_secret_access_key=os.getenv("S3_SECRET_KEY")
)
BUCKET_NAME = os.getenv("S3_BUCKET", "downloadino-files")

def upload_to_s3(file_obj, s3_key, content_type):
    try:
        s3_client.upload_fileobj(
            file_obj,
            BUCKET_NAME,
            s3_key,
            ExtraArgs={"ContentType": content_type}
        )
        return True
    except Exception as e:
        print(f"S3 Upload Error: {e}")
        return False

def get_presigned_url(s3_key, is_raw=False):
    # If raw, we want it to display in browser. If not, trigger download.
    params = {'Bucket': BUCKET_NAME, 'Key': s3_key}
    if not is_raw:
        params['ResponseContentDisposition'] = 'attachment'
        
    return s3_client.generate_presigned_url('get_object', Params=params, ExpiresIn=3600)

def delete_from_s3(s3_key):
    s3_client.delete_object(Bucket=BUCKET_NAME, Key=s3_key)