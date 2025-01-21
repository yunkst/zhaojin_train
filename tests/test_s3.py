import pytest

from conf import get_config
from plugins.logger import setup_logger
from plugins.s3connector import S3Connector

pytest_plugins = ("pytest_asyncio",)


conf = get_config()
logger = setup_logger()


def test_s3connector():
    s3conn = S3Connector(conf.s3connector, logger)

    if s3conn.conn is None:
        return

    bucket, fnm, binary = "txtxtxtxt1", "txtxtxtxt1", b"_t@123534@@1"
    s3conn.put(bucket, fnm, binary)
    assert s3conn.get(bucket, fnm) == binary


@pytest.mark.asyncio
async def test_async_s3connector():
    s3conn = S3Connector(conf.s3connector, logger)

    await s3conn.init()

    if s3conn.aconn is None:
        return

    bucket, fnm, binary = "txtxtxtxt1", "txtxtxtxt1", b"_t@123534@@1"
    await s3conn.aput(bucket, fnm, binary)
    res = await s3conn.aget(bucket, fnm)
    assert res == binary
