import boto3
from botocore.exceptions import NoCredentialsError, ClientError
import os 
import json
from dotenv import load_dotenv
import io
import tempfile

class S3BucketClient:
    _instance = None
    

    load_dotenv(dotenv_path="secret.env")
    

    DEFAULT_BUCKET_NAME = os.environ.get("S3_BUCKET")
    #Linux will not remove temp files at run time so it's safe to have a singleton 
    def __new__(cls, *args, **kwargs):

        if cls._instance is None:
            cls._instance = super(S3BucketClient, cls).__new__(cls)
        return cls._instance

    def __init__(self,
                  host=os.environ.get("S3_ENDPOINT"), 
                  access_key=os.environ.get("S3_ACCESS_KEY"), 
                  secret_key=os.environ.get("S3_SECRET_KEY"),
                  cert=os.environ.get("S3_SSL_CERT", "").strip()
                 ):
        
     
        if hasattr(self, '_initialized') and self._initialized:
            return

        self.host = host
        

        self.cert_path = None
        
        if cert:
            possible_path = cert
            
            if os.path.exists(possible_path):
                self.cert_path = possible_path
                print(f"Using SSL Certificate from: {self.cert_path}")
            else:
                print(f"WARNING: Certificate not found at {possible_path}. Defaulting to standard SSL.")

        self.__client = boto3.client('s3',
            endpoint_url=host,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            # path is set else true 
            verify=(self.cert_path if self.cert_path else True)
        )
        
        self._initialized = True

    def get_client(self):
        return self.__client

    def create_bucket_if_not_exists(self, bucket_name=DEFAULT_BUCKET_NAME):
        try:
            self.__client.head_bucket(Bucket=bucket_name)
            return "Bucket already found"
        except ClientError:
            print("Bucket not found. Creating new bucket...")
            self.__client.create_bucket(Bucket = bucket_name)
            #set public get policy on the bucket
            self.__client.put_public_access_block(
                Bucket=bucket_name
            )
            self.__client.put_bucket_cors(
                Bucket=bucket_name,
                CORSConfiguration={
                    'CORSRules': [
                        {
                            'AllowedHeaders': ['*'],
                            'AllowedMethods': ['GET', 'PUT', 'POST', 'DELETE', 'HEAD'],
                            'AllowedOrigins': ['*'],
                            'MaxAgeSeconds': 3000
                        }
                    ]
                }
            )
            #maybe imnplement a presigned api later 

            policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"AWS": "*"},
                        "Action": ["s3:GetObject"],
                        "Resource": [f"arn:aws:s3:::{bucket_name}/*"],
                    },
                ],
            }

            self.__client.put_bucket_policy(Bucket = bucket_name, Policy = json.dumps(policy))



    def upload(self, object_name, data, content_type="application/octet-stream", bucket_name =DEFAULT_BUCKET_NAME, return_flashblade_url = True):
        if not isinstance(data, bytes):
            return "Error: The 'data' parameter must be of type bytes."

        try:
            # Ensure the bucket exists
            self.__client.head_bucket(Bucket = bucket_name)
                

            # Convert the bytes data into a file-like object (a stream)
            data_stream = io.BytesIO(data)
        

            self.__client.put_object(
               Bucket =  bucket_name,
                Key = object_name,
                Body=data_stream,
               
                ContentType=content_type
            )

            # Construct the public URL accessible through frontend proxy
        #might need to change if its' flashblade
            if return_flashblade_url:
                url = f"{self.host}/{bucket_name}/{object_name}"
            else:
                url = f"https://{bucket_name}.s3.amazonaws.com/{object_name}"
            
            return url

        except Exception as e:
            return f"An error occurred during upload: {e}"

    def delete(self, object_name, bucket_name = DEFAULT_BUCKET_NAME):
      
        try:
            self.__client.delete_object(Bucket = bucket_name, Key = object_name)
            return f"Object '{object_name}' deleted successfully from bucket '{bucket_name}'."
        except Exception as e:
            return f"An error occurred during deletion: {e}"
        
    def generate_presigned_url(self, url ,expiration=3600 ,bucket_name = DEFAULT_BUCKET_NAME):
        try:
            object_name = self.extract_object(url)
            response = self.__client.generate_presigned_url('get_object',
                                                            Params={'Bucket': bucket_name,
                                                                    'Key': object_name},
                                                            ExpiresIn=expiration)
            return response
        except Exception as e:
            print(f"An error occurred while generating presigned URL: {e}")
            return None
        
    def extract_object(self, url):
        # Assumes URL format is https://bucket-name.s3.amazonaws.com/object-key

        parts = url.split('/')
        object_key = parts[-1]
        return object_key
   


   

    

    
