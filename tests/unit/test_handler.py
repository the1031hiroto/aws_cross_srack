import os
import json
import datetime
import pytest
import botocore
import boto3
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException
from crawler import app

d_now = datetime.datetime.now()
S3_ENDPOINT_URL = os.getenv("S3_ENDPOINT_URL")
CRAWL_URL = os.getenv("CRAWL_URL")
CRAWL_URL_ID = os.getenv("CRAWL_URL_ID")
BUCKET_NAME = os.getenv("BUCKET_NAME")
DIRECTORY = os.getenv("DIRECTORY")
SQS_EVENT_BODY = {
    "url": CRAWL_URL,
    "crawl_url_id": CRAWL_URL_ID,
    "bucket_name": BUCKET_NAME,
    "directory": DIRECTORY,
}

s3 = boto3.resource("s3", endpoint_url=S3_ENDPOINT_URL)


@pytest.fixture(scope="session")
def bucket():
    """ Generates Bucket"""
    s3.create_bucket(Bucket=BUCKET_NAME)


@pytest.fixture()
def sqs_event():
    """ Generates SQS Event"""

    return {
        "Records": [
            {
                "messageId": "19dd0b57-b21e-4ac1-bd88-01bbb068cb78",
                "receiptHandle": "MessageReceiptHandle",
                "body": '{"url": "https://tenbaggercreation.com", "crawl_url_id": 1234, "bucket_name": "minael.jp", "directory": "minique/crawled/" }',
                "attributes": {
                    "ApproximateReceiveCount": "1",
                    "SentTimestamp": "1523232000000",
                    "SenderId": "123456789012",
                    "ApproximateFirstReceiveTimestamp": "1523232000001",
                },
                "messageAttributes": {},
                "md5OfBody": "7b270e59b47ff90a553787216d55d91d",
                "eventSource": "aws:sqs",
                "eventSourceARN": "arn:aws:sqs:us-east-1:123456789012:MyQueue",
                "awsRegion": "us-east-1",
            }
        ]
    }


def test_lambda_handler(sqs_event, bucket, mocker):
    """Lambda呼び出しテスト
    Lambdaを呼び出して想定のレスポンスがあることを確認
    """

    sqs_event["Records"][0]["body"] = json.dumps(SQS_EVENT_BODY)

    ret = app.lambda_handler(sqs_event, "")
    data = json.loads(ret["body"])

    assert ret["statusCode"] == 200
    assert "url" in ret["body"]
    assert data["url"] == CRAWL_URL


def test_s3_bucket(sqs_event, mocker):
    """s3バケット作成テスト"""

    testBucketName = "test-create-bucket-{}".format(d_now.strftime("%Y%m%d%H%M%S"))

    # バケットが既存でないことを確認
    assert testBucketName not in [bucket.name for bucket in s3.buckets.all()]

    # バケット作成
    s3.create_bucket(Bucket=testBucketName)

    # バケットが作成されたことを確認
    assert testBucketName in [bucket.name for bucket in s3.buckets.all()]


def test_s3_object(sqs_event, mocker):
    """s3オブジェクト作成テスト"""

    testBucketName = "test-bucket-{}".format(d_now.strftime("%Y%m%d%H%M%S"))
    testObjectName = "test-object-{}".format(d_now.strftime("%Y%m%d%H%M%S"))

    # バケット作成
    s3.create_bucket(Bucket=testBucketName)

    # オブジェクトが既存でないことを確認
    assert testObjectName not in [
        s3_object.name for s3_object in s3.Bucket(testBucketName).objects.all()
    ]

    # オブジェクト作成
    obj = s3.Object(testBucketName, testObjectName)
    obj.put(Body=open("tests/unit/test.html", "rb"), ContentType="text/html")

    # オブジェクト取得
    obj = s3.Object(testBucketName, testObjectName)
    response = obj.get()
    soup = BeautifulSoup(response["Body"].read(), "html.parser")

    assert soup.find("title").text == "s3テスト"


def test_lambda_handler_s3(sqs_event, mocker):
    """Lambdaでs3保存テスト"""

    now = datetime.datetime.now()

    sqs_event["Records"][0]["body"] = json.dumps(SQS_EVENT_BODY)

    # Lambda呼び出し
    lambda_response = app.lambda_handler(sqs_event, "")
    json_load = json.loads(lambda_response["body"])
    key_name = json_load["key_name"]

    # オブジェクト取得
    obj = s3.Object(BUCKET_NAME, key_name)
    response = obj.get()
    soup = BeautifulSoup(response["Body"].read(), "html.parser")

    assert lambda_response["statusCode"] == 200
    assert str(CRAWL_URL_ID) + "_" + now.strftime("%Y%m%d%H%M") in key_name
    assert soup.find("title").text == "s3テスト"


def test_lambda_handler_s3_with_exception(sqs_event, mocker):
    """Lambdaでs3保存エラーテスト"""

    SQS_EVENT_BODY["bucket_name"] = "BUCKET_NAME"
    sqs_event["Records"][0]["body"] = json.dumps(SQS_EVENT_BODY)

    with pytest.raises(botocore.exceptions.ClientError):
        app.lambda_handler(sqs_event, "")


def test_timeout(sqs_event, mocker):
    """タイムアウトテスト
    Dockerでseleniumのタイムアウト時間を超えるnodeを立ち上げてテストする。
    """

    SQS_EVENT_BODY["url"] = os.getenv("SLOW_RESPONCE_URL")
    SQS_EVENT_BODY["crawl_url_id"] = "1235"
    sqs_event["Records"][0]["body"] = json.dumps(SQS_EVENT_BODY)

    with pytest.raises(TimeoutException):
        app.lambda_handler(sqs_event, "")
