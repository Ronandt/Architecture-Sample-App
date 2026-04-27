import io
import logging
import os

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError, ConnectTimeoutError, ReadTimeoutError

from shared.config import settings
from shared.exceptions import StorageError, StorageTimeout

logger = logging.getLogger(__name__)


class S3BucketClient:
    DEFAULT_BUCKET_NAME = settings.S3_BUCKET

    def __init__(self):
        host = settings.S3_ENDPOINT
        access_key = settings.S3_ACCESS_KEY.get_secret_value()
        secret_key = settings.S3_SECRET_KEY.get_secret_value()
        cert = settings.S3_SSL_CERT.strip()

        self.host = host
        self.cert_path = None

        if cert:
            if os.path.exists(cert):
                self.cert_path = cert
                logger.info("Using SSL Certificate from: %s", self.cert_path)
            else:
                logger.warning(
                    "Certificate not found at %s. Defaulting to standard SSL.", cert
                )

        self.__client = boto3.client(
            "s3",
            endpoint_url=host,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            verify=(self.cert_path if self.cert_path else True),
            config=Config(
                connect_timeout=settings.S3_CONNECT_TIMEOUT,
                read_timeout=settings.S3_READ_TIMEOUT,
                retries={"max_attempts": 0},
            ),
        )

    def get_client(self):
        return self.__client

    # ------------------------------------------------------------------
    # Bucket management - Use this for development only
    # ------------------------------------------------------------------

    def create_bucket_if_not_exists(self, bucket_name=DEFAULT_BUCKET_NAME):
        try:
            self.__client.head_bucket(Bucket=bucket_name)
            return "Bucket already found"
        except ClientError:
            logger.info("Bucket %s not found, creating...", bucket_name)
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
            self.__client.put_bucket_policy(Bucket=bucket_name)

    # ------------------------------------------------------------------
    # Health
    # ------------------------------------------------------------------

    def ping(self, bucket_name=DEFAULT_BUCKET_NAME) -> None:
        """Raise StorageUnavailable if S3 is unreachable or the bucket does not exist."""
        try:
            self.__client.head_bucket(Bucket=bucket_name)
        except (ConnectTimeoutError, ReadTimeoutError):
            raise StorageTimeout("S3 is not responding")
        except ClientError as e:
            code = e.response["Error"]["Code"]
            if code in ("404", "NoSuchBucket"):
                raise StorageError("S3 bucket does not exist", {"bucket": bucket_name})
            raise StorageError("S3 health check failed", {"reason": str(e)})
        except Exception as e:
            raise StorageError("S3 is unavailable", {"reason": str(e)})

    # ------------------------------------------------------------------
    # Object operations
    # ------------------------------------------------------------------

    def _build_object_url(self, bucket_name: str, object_name: str) -> str:
        if self.host and "amazonaws.com" not in self.host:
            return f"{self.host}/{bucket_name}/{object_name}"
        return f"https://{bucket_name}.s3.amazonaws.com/{object_name}"

    def upload(
        self,
        object_name: str,
        data: bytes,
        content_type: str = "application/octet-stream",
        bucket_name=DEFAULT_BUCKET_NAME,
        metadata: dict[str, str] | None = None,
    ) -> str:
        if not isinstance(data, bytes):
            raise StorageError("Upload data must be bytes")
        try:
            self.__client.head_bucket(Bucket=bucket_name)
            self.__client.put_object(
                Bucket=bucket_name,
                Key=object_name,
                Body=io.BytesIO(data),
                ContentType=content_type,
                **({"Metadata": metadata} if metadata else {}),
            )
            return self._build_object_url(bucket_name, object_name)
        except StorageError:
            raise
        except (ConnectTimeoutError, ReadTimeoutError) as e:
            logger.error("Upload timed out for '%s': %s", object_name, e)
            raise StorageTimeout("Upload timed out", {"object": object_name})
        except Exception as e:
            logger.error("Upload failed for '%s': %s", object_name, e)
            raise StorageError(
                "Upload failed", {"object": object_name, "reason": str(e)}
            )

    def delete(self, object_name: str, bucket_name=DEFAULT_BUCKET_NAME) -> None:
        try:
            self.__client.delete_object(Bucket=bucket_name, Key=object_name)
        except (ConnectTimeoutError, ReadTimeoutError) as e:
            logger.error("Delete timed out for '%s': %s", object_name, e)
            raise StorageTimeout("Delete timed out", {"object": object_name})
        except Exception as e:
            logger.error("Delete failed for '%s': %s", object_name, e)
            raise StorageError(
                "Delete failed", {"object": object_name, "reason": str(e)}
            )

    def generate_presigned_url(
        self, object_key: str, expiration: int = 3600, bucket_name=DEFAULT_BUCKET_NAME
    ) -> str:
        try:
            return self.__client.generate_presigned_url(
                "get_object",
                Params={"Bucket": bucket_name, "Key": object_key},
                ExpiresIn=expiration,
            )
        except (ConnectTimeoutError, ReadTimeoutError) as e:
            logger.error("Presigned URL timed out for '%s': %s", object_key, e)
            raise StorageTimeout(
                "Presigned URL generation timed out", {"object": object_key}
            )
        except Exception as e:
            logger.error("Presigned URL generation failed for '%s': %s", object_key, e)
            raise StorageError(
                "Failed to generate presigned URL",
                {"object": object_key, "reason": str(e)},
            )

    def list_objects(
        self, prefix: str = "", bucket_name=DEFAULT_BUCKET_NAME
    ) -> list[str]:
        """List object keys in a bucket, optionally filtered by prefix."""
        try:
            response = self.__client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
            return [obj["Key"] for obj in response.get("Contents", [])]
        except (ConnectTimeoutError, ReadTimeoutError) as e:
            logger.error("List objects timed out: %s", e)
            raise StorageTimeout("List objects timed out", {"prefix": prefix})
        except Exception as e:
            logger.error("List objects failed: %s", e)
            raise StorageError(
                "Failed to list objects", {"prefix": prefix, "reason": str(e)}
            )

    def copy_object(
        self, source_key: str, dest_key: str, bucket_name=DEFAULT_BUCKET_NAME
    ) -> None:
        """Copy an object to a new key within the same bucket."""
        try:
            self.__client.copy_object(
                CopySource={"Bucket": bucket_name, "Key": source_key},
                Bucket=bucket_name,
                Key=dest_key,
            )
        except (ConnectTimeoutError, ReadTimeoutError) as e:
            logger.error(
                "Copy timed out from '%s' to '%s': %s", source_key, dest_key, e
            )
            raise StorageTimeout(
                "Copy timed out", {"source": source_key, "dest": dest_key}
            )
        except Exception as e:
            logger.error("Copy failed from '%s' to '%s': %s", source_key, dest_key, e)
            raise StorageError(
                "Copy failed",
                {"source": source_key, "dest": dest_key, "reason": str(e)},
            )

    def get_object(self, key: str, bucket_name=DEFAULT_BUCKET_NAME) -> bytes:
        """Download an object and return its content as bytes."""
        try:
            response = self.__client.get_object(Bucket=bucket_name, Key=key)
            return response["Body"].read()
        except (ConnectTimeoutError, ReadTimeoutError) as e:
            logger.error("Get object timed out for '%s': %s", key, e)
            raise StorageTimeout("Get object timed out", {"object": key})
        except Exception as e:
            logger.error("Get object failed for '%s': %s", key, e)
            raise StorageError(
                "Failed to get object", {"object": key, "reason": str(e)}
            )

    def object_exists(self, key: str, bucket_name=DEFAULT_BUCKET_NAME) -> bool:
        """Return True if the key exists in the bucket (HEAD request)."""
        try:
            self.__client.head_object(Bucket=bucket_name, Key=key)
            return True
        except ClientError:
            return False

    def delete_objects(self, keys: list[str], bucket_name=DEFAULT_BUCKET_NAME) -> None:
        """Batch-delete multiple objects in a single API call (max 1000 per call)."""
        if not keys:
            return
        try:
            self.__client.delete_objects(
                Bucket=bucket_name,
                Delete={"Objects": [{"Key": k} for k in keys], "Quiet": True},
            )
        except (ConnectTimeoutError, ReadTimeoutError) as e:
            logger.error("Batch delete timed out: %s", e)
            raise StorageTimeout("Batch delete timed out", {"count": len(keys)})
        except Exception as e:
            logger.error("Batch delete failed: %s", e)
            raise StorageError(
                "Batch delete failed", {"count": len(keys), "reason": str(e)}
            )

    def get_object_metadata(self, key: str, bucket_name=DEFAULT_BUCKET_NAME) -> dict:
        """
        Return object metadata without downloading the body.
        Includes: ContentLength, ContentType, LastModified, ETag, Metadata.
        """
        try:
            response = self.__client.head_object(Bucket=bucket_name, Key=key)
            return {
                "content_length": response.get("ContentLength"),
                "content_type": response.get("ContentType"),
                "last_modified": response.get("LastModified"),
                "etag": response.get("ETag", "").strip('"'),
                "metadata": response.get("Metadata", {}),
            }
        except (ConnectTimeoutError, ReadTimeoutError) as e:
            logger.error("Metadata fetch timed out for '%s': %s", key, e)
            raise StorageTimeout("Metadata fetch timed out", {"object": key})
        except ClientError as e:
            code = e.response["Error"]["Code"]
            if code == "404":
                raise StorageError("Object not found", {"object": key})
            raise StorageError(
                "Failed to get metadata", {"object": key, "reason": str(e)}
            )
        except Exception as e:
            logger.error("Metadata fetch failed for '%s': %s", key, e)
            raise StorageError(
                "Failed to get metadata", {"object": key, "reason": str(e)}
            )

    def generate_presigned_upload_url(
        self,
        object_key: str,
        content_type: str = "application/octet-stream",
        expiration: int = 300,
        bucket_name=DEFAULT_BUCKET_NAME,
    ) -> str:
        """
        Generate a presigned PUT URL for direct browser → S3 uploads.
        The client must send the file as the raw request body with the matching Content-Type header.
        Expires in 5 minutes by default.
        """
        try:
            return self.__client.generate_presigned_url(
                "put_object",
                Params={
                    "Bucket": bucket_name,
                    "Key": object_key,
                    "ContentType": content_type,
                },
                ExpiresIn=expiration,
                HttpMethod="PUT",
            )
        except (ConnectTimeoutError, ReadTimeoutError) as e:
            logger.error("Presigned upload URL timed out for '%s': %s", object_key, e)
            raise StorageTimeout(
                "Presigned upload URL generation timed out", {"object": object_key}
            )
        except Exception as e:
            logger.error(
                "Presigned upload URL generation failed for '%s': %s", object_key, e
            )
            raise StorageError(
                "Failed to generate presigned upload URL",
                {"object": object_key, "reason": str(e)},
            )

    def move_object(
        self, source_key: str, dest_key: str, bucket_name=DEFAULT_BUCKET_NAME
    ) -> None:
        """Move (rename) an object by copying it then deleting the source."""
        self.copy_object(source_key, dest_key, bucket_name)
        self.delete(source_key, bucket_name)

    # ------------------------------------------------------------------
    # Bucket operations
    # ------------------------------------------------------------------

    def bucket_exists(self, bucket_name=DEFAULT_BUCKET_NAME) -> bool:
        """Return True if the bucket exists and is accessible."""
        try:
            self.__client.head_bucket(Bucket=bucket_name)
            return True
        except ClientError:
            return False

    def set_bucket_lifecycle(
        self,
        days_until_expiry: int,
        prefix: str = "",
        bucket_name=DEFAULT_BUCKET_NAME,
    ) -> None:
        """
        Set a lifecycle rule that auto-deletes objects after N days.
        Useful for temporary uploads, drafts, or cache objects.
        Pass prefix='' to apply to all objects, or e.g. 'tmp/' for a subfolder.
        """
        try:
            self.__client.put_bucket_lifecycle_configuration(
                Bucket=bucket_name,
                LifecycleConfiguration={
                    "Rules": [
                        {
                            "ID": f"expire-after-{days_until_expiry}d",
                            "Status": "Enabled",
                            "Filter": {"Prefix": prefix},
                            "Expiration": {"Days": days_until_expiry},
                        }
                    ]
                },
            )
        except (ConnectTimeoutError, ReadTimeoutError) as e:
            logger.error("Set lifecycle timed out: %s", e)
            raise StorageTimeout("Set lifecycle timed out", {"bucket": bucket_name})
        except Exception as e:
            logger.error("Set lifecycle failed: %s", e)
            raise StorageError(
                "Failed to set lifecycle policy",
                {"bucket": bucket_name, "reason": str(e)},
            )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _extract_key(self, url: str) -> str:
        """Extract the object key from a full object URL by stripping the host+bucket prefix."""
        if self.host:
            prefix = f"{self.host}/{self.DEFAULT_BUCKET_NAME}/"
            if url.startswith(prefix):
                return url[len(prefix):]
        # AWS virtual-hosted style: https://<bucket>.s3.amazonaws.com/<key>
        parts = url.split("/", 3)
        return parts[3] if len(parts) > 3 else url
