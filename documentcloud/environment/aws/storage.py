# Third Party
import boto3
import environ
import requests
import smart_open
from botocore.client import Config

env = environ.Env()


class AwsStorage:
    def __init__(self, resource_kwargs=None, minio=False):

        self.resource_kwargs = {} if resource_kwargs is None else resource_kwargs
        if "config" not in self.resource_kwargs:
            self.resource_kwargs["config"] = Config(signature_version="s3v4")
        self.s3_resource = boto3.resource("s3", **self.resource_kwargs)
        self.s3_client = boto3.client("s3", **self.resource_kwargs)
        self.minio = minio

    def bucket_key(self, file_name):
        return file_name.split("/", 1)

    def size(self, file_name):
        bucket, key = self.bucket_key(file_name)
        bucket = self.s3_resource.Bucket(bucket)
        return bucket.Object(key).content_length

    def open(self, file_name, mode="rb"):

        return smart_open.open(
            f"s3://{file_name}",
            mode,
            transport_params={"resource_kwargs": self.resource_kwargs},
        )

    def presign_url(self, file_name, method_name):
        bucket, key = self.bucket_key(file_name)
        return self.s3_client.generate_presigned_url(
            method_name, Params={"Bucket": bucket, "Key": key}, ExpiresIn=300
        )

    def exists(self, file_name):
        # https://www.peterbe.com/plog/fastest-way-to-find-out-if-a-file-exists-in-s3
        bucket, key = self.bucket_key(file_name)
        response = self.s3_client.list_objects_v2(Bucket=bucket, Prefix=key)
        for obj in response.get("Contents", []):
            if obj["Key"] == key:
                return True
        return False

    def fetch_url(self, url, file_name):
        bucket, key = self.bucket_key(file_name)
        with requests.get(url, stream=True) as response:
            response.raise_for_status()
            self.s3_resource.Bucket(bucket).upload_fileobj(response.raw, key)

    def delete(self, file_prefix):
        bucket, prefix = self.bucket_key(file_prefix)
        bucket = self.s3_resource.Bucket(bucket)
        keys = [{"Key": obj.key} for obj in bucket.objects.filter(Prefix=prefix)]
        bucket.delete_objects(Delete={"Objects": keys})

    def set_access(self, file_prefix, access):
        if self.minio:
            # minio does not support object ACLs
            return
        acls = {"public": "public-read", "private": "private"}
        bucket, prefix = self.bucket_key(file_prefix)
        bucket = self.s3_resource.Bucket(bucket)
        for obj in bucket.objects.filter(Prefix=prefix):
            obj.Acl().put(ACL=acls[access])


storage = AwsStorage()
minio_storage = AwsStorage(
    {
        "endpoint_url": env.str("MINIO_URL"),
        "aws_access_key_id": env.str("MINIO_ACCESS_KEY"),
        "aws_secret_access_key": env.str("MINIO_SECRET_KEY"),
        "config": Config(signature_version="s3v4"),
        "region_name": "us-east-1",
    },
    minio=True,
)