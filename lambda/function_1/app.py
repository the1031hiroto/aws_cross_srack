import os
import json
import datetime
import botocore
import boto3
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
import logging

logger = logging.getLogger()
level_name = os.environ.get("LOG_LEVEL")
level = logging.getLevelName(level_name)
if not isinstance(level, int):
    level = logging.INFO
logger.setLevel(level)


def lambda_handler(event, context):
    """対象URLをクロールしてS3に保存
    Args:
        event (obj): Lambdaが受け取るイベント
        context (obj): コンテキスト情報
    Returns:
        obj: [description]
    """
    logger.info("event: {}".format(event))

    bucket_name = os.getenv("S3_BUCKET_NAME")
    crawled_file_directory = os.getenv("S3_PREFIX")

    crawl_url_id = event["crawl_url_id"]
    url = event["url"]
    prefix = "{}{}/crawled.html".format(crawled_file_directory, crawl_url_id)

    crawled_text = crawler(url)
    result = save_to_s3(bucket_name, prefix, crawled_text)

    return_body = {
        "original_input": event.get("original_input"),
        "crawl_url_id": crawl_url_id,
        "bucket_name": bucket_name,
        "prefix": prefix,
        "crawled_version_id": result["VersionId"],
    }

    logger.info("return: {}".format(return_body))

    return return_body


def crawler(url):
    """対象URLをクロールしてHTMLを返却
    Args:
        url (str): クロールするURL
    Raises:
        Exception: ステータスコードが200以外はエラー
    Returns:
        str: クロール結果HTML
    """

    HEADLESS_CHROMIUM_PATH = os.getenv("HEADLESS_CHROMIUM_PATH")
    CHROME_DRIVER_PATH = os.getenv("CHROME_DRIVER_PATH")
    PAGE_LOAD_TIMEOUT = os.getenv("PAGE_LOAD_TIMEOUT")

    options = webdriver.ChromeOptions()
    options.binary_location = HEADLESS_CHROMIUM_PATH
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--single-process")

    # chrome_optionsだとpytestではwarning出るが、optionsだとLambdaでは動かない
    # driver = webdriver.Chrome(executable_path=CHROME_DRIVER_PATH, options=options)
    driver = webdriver.Chrome(executable_path=CHROME_DRIVER_PATH, chrome_options=options)
    driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)

    driver.get(url)

    crawled_text = driver.page_source

    return crawled_text


def save_to_s3(bucket_name, prefix, target_file):
    """S3に保存
    Args:
        bucket_name (str): バケット名
        prefix (str): 保存先
        target_file (str): 保存するファイル
    Raises:
        e: S3への接続エラー
    """

    S3_ENDPOINT_URL = os.getenv("S3_ENDPOINT_URL")

    if S3_ENDPOINT_URL:
        s3 = boto3.resource("s3", endpoint_url=S3_ENDPOINT_URL)
    else:
        s3 = boto3.resource("s3")

    try:
        obj = s3.Object(bucket_name, prefix)
        result = obj.put(Body=target_file, ContentType="text/html")
    except botocore.exceptions.ClientError as e:
        raise e

    return result
