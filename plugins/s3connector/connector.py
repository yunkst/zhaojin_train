from logging import Logger

import aioboto3
import boto3
from botocore.exceptions import ClientError
from fastapi import FastAPI, Request

from .config import S3Config
from .exception import S3Exception
from .retry import retry


def get_s3conn(request: Request) -> "S3Connector":
    return request.app.state.s3conn  # type: ignore


class S3Connector(object):  # noqa: UP004
    """S3Connector 是用于连接和操作 Amazon S3 存储服务的工具类。它提供了上传、下载以及管理 S3 对象的方法。"""

    def __init__(self, config: S3Config, logger: Logger):  # noqa: D107
        self.conf = config
        self.conn = boto3.client(  # type: ignore
            "s3",
            aws_access_key_id=self.conf.user,
            aws_secret_access_key=self.conf.password,
            region_name=self.conf.region_name,
            endpoint_url=self.conf.host,
        )
        self.aconn = None
        self.logger = logger

    async def init(self):
        if self.aconn is None:  # type: ignore
            async with aioboto3.Session().client(  # type: ignore
                "s3",
                aws_access_key_id=self.conf.user,
                aws_secret_access_key=self.conf.password,
                region_name=self.conf.region_name,
                endpoint_url=self.conf.host,
            ) as client:
                self.aconn = client

    async def destory(self):
        if self.aconn is not None:
            await self.aconn.close()  # type: ignore
            self.aconn = None

    def mount_app(self, app: FastAPI) -> None:
        """挂载到 FastAPI 应用.

        Parameters
        ----------
        app : FastAPI
            FastAPI 应用.

        """
        app.state.s3conn = self

    @retry(times=3, sleep_time=1.0)
    def bucket_exists(self, bucket_name: str):  # noqa: D102
        try:
            self.conn.head_bucket(Bucket=bucket_name)  # type: ignore
            return True  # Bucket exists
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return False  # Bucket does not exist
            raise S3Exception(e)
        except Exception as e:
            raise S3Exception(e)

    @retry(times=3, sleep_time=1.0)
    def put(self, bucket: str, fnm: str, binary: bytes) -> dict | None:  # type: ignore  # noqa: D102
        try:
            if not self.bucket_exists(bucket):
                self.conn.create_bucket(Bucket=bucket)  # type: ignore
            return self.conn.put_object(Bucket=bucket, Key=fnm, Body=binary)  # type: ignore
        except Exception as e:
            self.logger.warning(f"fail put {bucket}/{fnm}. Retrying: " + str(e))  # noqa: G003
            raise

    @retry(times=3, sleep_time=1.0)
    def rm(self, bucket: str, fnm: str):  # noqa: D102
        try:
            self.conn.delete_object(Bucket=bucket, Key=fnm)  # type: ignore
        except Exception as e:
            raise S3Exception(f"Fail rm {bucket}/{fnm}: " + str(e))

    @retry(times=3, sleep_time=1.0)
    def get(self, bucket: str, fnm: str) -> bytes | None:  # noqa: D102
        try:
            r = self.conn.get_object(Bucket=bucket, Key=fnm)  # type: ignore
            return r["Body"].read()  # type: ignore
        except Exception as e:
            self.logger.warning(f"Fail get {bucket}/{fnm}. Retrying: " + str(e))  # noqa: G003
            raise

    @retry(times=3, sleep_time=1.0)
    def obj_exist(self, bucket: str, fnm: str):  # noqa: D102
        try:
            _ = self.conn.head_object(Bucket=bucket, Key=fnm)  # type: ignore
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return False  # Object does not exist
            raise S3Exception(f"Fail obj_exist {bucket}/{fnm}: " + str(e))  # type: ignore
        except Exception as e:
            raise S3Exception(f"Fail obj_exist {bucket}/{fnm}: " + str(e))

    @retry(times=3, sleep_time=1.0)
    def ls(self, bucket: str, file_prefix: str = "") -> list[str] | None:
        """将桶内Key视作POSIX文件路径时，ls将会显示file_prefix文件夹下的所有文件和文件夹名"""

        def filter_path(paths: list[str], prefix: str) -> list[str]:
            ret = []
            for p in paths:
                if p.startswith(prefix):
                    idx = p[len(prefix) :].find("/")
                    ret.append(p[len(prefix) :][:idx] if idx > 0 else p[len(prefix) :])  # type: ignore
            return list(set(ret))  # type: ignore

        try:
            res = self.conn.list_objects(Bucket=bucket, Prefix=file_prefix)  # type: ignore
            return filter_path([r["Key"] for r in res["Contents"]], file_prefix)

        except Exception as e:
            self.logger.warning(f"Fail list objects {bucket}/{file_prefix}. Retrying: " + str(e))  # noqa: G003
            raise

    @retry(times=3, sleep_time=1.0)
    def get_presigned_url(self, bucket: str, fnm: str, expires: int = 3600) -> str | None:
        """Generate a presigned URL to share an S3 object

        :param bucket: string
        :param fnm: string
        :param expires: Time in seconds for the presigned URL to remain valid
        :return: Presigned URL as string. If error, returns None.
        """
        try:
            return self.conn.generate_presigned_url(  # type: ignore
                "get_object", Params={"Bucket": bucket, "Key": fnm}, ExpiresIn=expires
            )  # type: ignore
        except Exception as e:
            self.logger.warning(f"Fail get GET url {bucket}/{fnm}. Retrying: " + str(e))  # noqa: G003
            raise

    @retry(times=3, sleep_time=1.0)
    def put_presigned_url(self, bucket: str, fnm: str, expires: int = 3600) -> str | None:
        """Generate a presigned URL S3 POST request to upload a file

        :param bucket: string
        :param fnm: string
        :param expires: Time in seconds for the presigned URL to remain valid
        :return: url: URL to put to
        :return: None if error.
        """
        try:
            return self.conn.generate_presigned_url(  # type: ignore
                "put_object", Params={"Bucket": bucket, "Key": fnm}, ExpiresIn=expires
            )  # type: ignore
        except Exception as e:
            self.logger.warning(f"Fail get PUT url {bucket}/{fnm}. Retrying: " + str(e))  # noqa: G003
            raise

    @retry(times=3, sleep_time=1.0)
    async def abucket_exists(self, bucket_name: str):  # noqa: D102
        try:
            await self.aconn.head_bucket(Bucket=bucket_name)  # type: ignore
            return True  # Bucket exists
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return False  # Bucket does not exist
            raise S3Exception(e)
        except Exception as e:
            raise S3Exception(e)

    async def aput(self, bucket: str, fnm: str, binary: bytes) -> dict | None:  # type: ignore  # noqa: D102
        try:
            if not await self.abucket_exists(bucket):
                await self.aconn.create_bucket(Bucket=bucket)  # type: ignore

            r = await self.aconn.put_object(Bucket=bucket, Key=fnm, Body=binary)  # type: ignore
            return r
        except Exception as e:
            self.logger.warning(f"fail put {bucket}/{fnm}. Retrying: " + str(e))  # noqa: G003
            raise

    @retry(times=3, sleep_time=1.0)
    async def arm(self, bucket: str, fnm: str):  # noqa: D102
        try:
            await self.aconn.delete_object(Bucket=bucket, Key=fnm)  # type: ignore
        except Exception as e:
            raise S3Exception(f"Fail rm {bucket}/{fnm}: " + str(e))

    @retry(times=3, sleep_time=1.0)
    async def aget(self, bucket: str, fnm: str) -> bytes | None:  # noqa: D102
        try:
            r = await self.aconn.get_object(Bucket=bucket, Key=fnm)  # type: ignore
            return await r["Body"].read()  # type: ignore
        except Exception as e:
            self.logger.warning(f"Fail get {bucket}/{fnm}. Retrying: " + str(e))  # noqa: G003
            raise

    @retry(times=3, sleep_time=1.0)
    async def als(self, bucket: str, file_prefix: str = "") -> list[str] | None:
        """将桶内Key视作POSIX文件路径时，ls将会显示file_prefix文件夹下的所有文件和文件夹名"""

        def filter_path(paths: list[str], prefix: str) -> list[str]:
            ret = []
            for p in paths:
                if p.startswith(prefix):
                    idx = p[len(prefix) :].find("/")
                    ret.append(p[len(prefix) :][:idx] if idx > 0 else p[len(prefix) :])  # type: ignore
            return list(set(ret))  # type: ignore

        try:
            res = await self.aconn.list_objects(Bucket=bucket, Prefix=file_prefix)  # type: ignore
            return filter_path([r["Key"] for r in res["Contents"]], file_prefix)

        except Exception as e:
            self.logger.warning(f"Fail list objects {bucket}/{file_prefix}. Retrying: " + str(e))  # noqa: G003
            raise

    @retry(times=3, sleep_time=1.0)
    async def aobj_exist(self, bucket: str, fnm: str):  # noqa: D102
        try:
            _ = await self.aconn.head_object(Bucket=bucket, Key=fnm)  # type: ignore
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return False  # Object does not exist
            raise S3Exception(f"Fail obj_exist {bucket}/{fnm}: " + str(e))  # type: ignore
        except Exception as e:
            raise S3Exception(f"Fail obj_exist {bucket}/{fnm}: " + str(e))

    @retry(times=3, sleep_time=1.0)
    async def aget_presigned_url(self, bucket: str, fnm: str, expires: int = 3600) -> str | None:
        """Generate a presigned URL to share an S3 object

        :param bucket: string
        :param fnm: string
        :param expires: Time in seconds for the presigned URL to remain valid
        :return: Presigned URL as string. If error, returns None.
        """
        try:
            return await self.aconn.generate_presigned_url(  # type: ignore
                "get_object", Params={"Bucket": bucket, "Key": fnm}, ExpiresIn=expires
            )  # type: ignore
        except Exception as e:
            self.logger.warning(f"Fail get GET url {bucket}/{fnm}. Retrying: " + str(e))  # noqa: G003
            raise

    @retry(times=3, sleep_time=1.0)
    async def aput_presigned_url(self, bucket: str, fnm: str, expires: int = 3600) -> str | None:
        """Generate a presigned URL S3 POST request to upload a file

        :param bucket: string
        :param fnm: string
        :param expires: Time in seconds for the presigned URL to remain valid
        :return: url: URL to put to
        :return: None if error.
        """
        try:
            return await self.aconn.generate_presigned_url(  # type: ignore
                "put_object", Params={"Bucket": bucket, "Key": fnm}, ExpiresIn=expires
            )  # type: ignore
        except Exception as e:
            self.logger.warning(f"Fail get PUT url {bucket}/{fnm}. Retrying: " + str(e))  # noqa: G003
            raise
