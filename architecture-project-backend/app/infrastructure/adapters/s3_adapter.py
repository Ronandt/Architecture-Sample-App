import boto3
from botocore.exceptions import ClientError
import os
import json
import io
from dotenv import load_dotenv


class S3BucketClient:
    _instance = None

    load_dotenv(dotenv_path="secret.env")

    DEFAULT_BUCKET_NAME = os.environ.get("S3_BUCKET")

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(S3BucketClient, cls).__new__(cls)
        return cls._instance

    def __init__(
        self,
        host=os.environ.get("S3_ENDPOINT"),
        access_key=os.environ.get("S3_ACCESS_KEY"),
        secret_key=os.environ.get("S3_SECRET_KEY"),
        cert=os.environ.get("S3_SSL_CERT", "").strip(),
    ):
        if hasattr(self, "_initialized") and self._initialized:
            return

        self.host = host
        self.cert_path = None

        if cert:
            if os.path.exists(cert):
                self.cert_path = cert
                print(f"Using SSL Certificate from: {self.cert_path}")
            else:
                print(f"WARNING: Certificate not found at {cert}. Defaulting to standard SSL.")

        self.__client = boto3.client(
            "s3",
            endpoint_url=host,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            verify=(self.cert_path if self.cert_path else True),
        )

        self._initialized = True

    def get_client(self):
        return self.__client

    # ------------------------------------------------------------------
    # Bucket management
    # ------------------------------------------------------------------

    def create_bucket_if_not_exists(self, bucket_name=DEFAULT_BUCKET_NAME):
        try:
            self.__client.head_bucket(Bucket=bucket_name)
            return "Bucket already found"
        except ClientError:
            print("Bucket not found. Creating new bucket...")
            self.__client.create_bucket(Bucket=bucket_name)
            self.__client.put_public_access_block(Bucket=bucket_name)
            self.__client.put_bucket_cors(
                Bucket=bucket_name,
                CORSConfiguration={
                    "CORSRules": [
                        {
                            "AllowedHeaders": ["*"],
                            "AllowedMethods": ["GET", "PUT", "POST", "DELETE", "HEAD"],
                            "AllowedOrigins": ["*"],
                            "MaxAgeSeconds": 3000,
                        }
                    ]
                },
            )
            policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"AWS": "*"},
                        "Action": ["s3:GetObject"],
                        "Resource": [f"arn:aws:s3:::{bucket_name}/*"],
                    }
                ],
            }
            self.__client.put_bucket_policy(Bucket=bucket_name, Policy=json.dumps(policy))

    # ------------------------------------------------------------------
    # Object operations
    # ------------------------------------------------------------------

    def upload(
        self,
        object_name: str,
        data: bytes,
        content_type: str = "application/octet-stream",
        bucket_name=DEFAULT_BUCKET_NAME,
        return_flashblade_url: bool = True,
    ) -> str:
        if not isinstance(data, bytes):
            return "Error: The 'data' parameter must be of type bytes."
        try:
            self.__client.head_bucket(Bucket=bucket_name)
            self.__client.put_object(
                Bucket=bucket_name,
                Key=object_name,
                Body=io.BytesIO(data),
                ContentType=content_type,
            )
            if return_flashblade_url:
                return f"{self.host}/{bucket_name}/{object_name}"
            return f"https://{bucket_name}.s3.amazonaws.com/{object_name}"
        except Exception as e:
            return f"An error occurred during upload: {e}"

    def delete(self, object_name: str, bucket_name=DEFAULT_BUCKET_NAME) -> str:
        try:
            self.__client.delete_object(Bucket=bucket_name, Key=object_name)
            return f"Object '{object_name}' deleted successfully from bucket '{bucket_name}'."
        except Exception as e:
            return f"An error occurred during deletion: {e}"

    def generate_presigned_url(
        self, url: str, expiration: int = 3600, bucket_name=DEFAULT_BUCKET_NAME
    ) -> str | None:
        try:
            object_name = self._extract_key(url)
            return self.__client.generate_presigned_url(
                "get_object",
                Params={"Bucket": bucket_name, "Key": object_name},
                ExpiresIn=expiration,
            )
        except Exception as e:
            print(f"An error occurred while generating presigned URL: {e}")
            return None

    def list_objects(self, prefix: str = "", bucket_name=DEFAULT_BUCKET_NAME) -> list[str]:
        """List object keys in a bucket, optionally filtered by prefix."""
        try:
            response = self.__client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
            return [obj["Key"] for obj in response.get("Contents", [])]
        except Exception as e:
            print(f"Error listing objects: {e}")
            return []

    def copy_object(
        self, source_key: str, dest_key: str, bucket_name=DEFAULT_BUCKET_NAME
    ) -> bool:
        """Copy an object to a new key within the same bucket."""
        try:
            self.__client.copy_object(
                CopySource={"Bucket": bucket_name, "Key": source_key},
                Bucket=bucket_name,
                Key=dest_key,
            )
            return True
        except Exception as e:
            print(f"Error copying object: {e}")
            return False

    def get_object(self, key: str, bucket_name=DEFAULT_BUCKET_NAME) -> bytes | None:
        """Download an object and return its content as bytes."""
        try:
            response = self.__client.get_object(Bucket=bucket_name, Key=key)
            return response["Body"].read()
        except Exception as e:
            print(f"Error getting object '{key}': {e}")
            return None

    def object_exists(self, key: str, bucket_name=DEFAULT_BUCKET_NAME) -> bool:
        """Return True if the key exists in the bucket (HEAD request)."""
        try:
            self.__client.head_object(Bucket=bucket_name, Key=key)
            return True
        except ClientError:
            return False

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _extract_key(self, url: str) -> str:
        """Extract the object key from a URL (last path segment)."""
        return url.split("/")[-1]
