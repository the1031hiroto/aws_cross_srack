import os
import json
import datetime
from bs4 import BeautifulSoup
import botocore
import boto3
from collections import deque
import difflib
import logging

logger = logging.getLogger()
level_name = os.environ.get("LOG_LEVEL")
level = logging.getLevelName(level_name)
if not isinstance(level, int):
    level = logging.INFO
logger.setLevel(level)


def lambda_handler(event, context):
    """最新２件のクロール結果に差分がある場合に差分ファイル保存
    Args:
        event (obj): Lambdaが受け取るイベント
        context (obj): コンテキスト情報
    Returns:
        obj: [description]
    """
    logger.info("event: {}".format(event))

    bucket_name = os.getenv("S3_BUCKET_NAME")
    s3_prefix = os.getenv("S3_PREFIX")

    check_type = event["check_type"]
    crawl_url_id = event["crawl_url_id"]
    crawled_file_prefix = "{}{}/crawled.html".format(s3_prefix, crawl_url_id)
    last_crawled_version_id = event["crawled_version_id"]

    return_body = {
        "original_input": event.get("original_input"),
        "crawl_url_id": crawl_url_id,
        "bucket_name": bucket_name,
        "crawled_file_prefix": crawled_file_prefix,
        "is_changed": False,
        "diff_file_prefix": None,
        "diff_version_id": None,
        "last_crawled_version_id": last_crawled_version_id,
    }

    current_html, incoming_html = get_html(bucket_name, crawled_file_prefix, last_crawled_version_id)

    if current_html is None or incoming_html is None:
        return return_body

    is_changed, diff_file = check_diff(current_html, incoming_html, check_type)

    if is_changed:
        diff_file_prefix = "{}{}/diff.html".format(s3_prefix, crawl_url_id)
        result = save_to_s3(bucket_name, diff_file_prefix, diff_file)

        return_body["diff_file_prefix"] = diff_file_prefix
        return_body["is_changed"] = is_changed
        return_body["diff_version_id"] = result["VersionId"]

    logger.info("return: {}".format(return_body))

    return return_body


def check_diff(current_html, incoming_html, check_type):
    """前回のクロールと差分があるか確認して差分ある場合差分ファイル作成して返却
    Args:
        current_html (str): [description]
        incoming_html (str): [description]
        check_type (str): [description]
    Returns:
        boolean: 差分があった場合はTrue
        str: 差分ファイル
    """

    current_soup = BeautifulSoup(current_html, "html.parser")
    for tag in current_soup.find_all(["iframe", "link", "meta", "script", "style"]):
        tag.decompose()

    incoming_soup = BeautifulSoup(incoming_html, "html.parser")
    for tag in incoming_soup.find_all(["iframe", "link", "meta", "script", "style"]):
        tag.decompose()

    # HTMLタグを除くテキスト差分確認
    if check_type == "only_text":
        current_text = current_soup.get_text()
        incoming_text = incoming_soup.get_text()

    # HTMLタグも含む差分確認
    elif check_type == "with_html_tag":
        current_text = current_soup.__str__()
        incoming_text = incoming_soup.__str__()

    s = difflib.SequenceMatcher(None, current_text, incoming_text)
    diff_ratio = round(s.quick_ratio(), 3)
    logger.info("diff ratio: {}".format(diff_ratio))

    # TODO: 範囲は要検討
    if 0.98 < diff_ratio:
        logger.info("Thewe were no diff. diff_ratio: {}".format(diff_ratio))
        return False, None

    logger.info("Thewe were diff. diff_ratio: {}".format(diff_ratio))

    # 差分ある場合、差分ファイル作成
    path_current_html = os.getenv("TMP_CURRENT_HTML_PATH")
    path_incoming_html = os.getenv("TMP_INCOMING_HTML_PATH")

    df = difflib.HtmlDiff()

    with open(path_current_html, mode="w+") as _current_html:
        _current_html.write(current_text)

    with open(path_incoming_html, mode="w+") as _incoming_html:
        _incoming_html.write(incoming_text)

    a = open(path_current_html)
    b = open(path_incoming_html)
    diff_file = df.make_file(a, b)

    a.close()
    b.close()

    os.remove(path_current_html)
    os.remove(path_incoming_html)

    return True, diff_file


def get_html(bucket_name, prefix, last_crawled_version_id):
    """S3に保存されたHTMLを最新2件取得
    Args:
        bucket_name ([type]): バケット名
        prefix ([type]): 取得先
    Raises:
        e: S3への接続エラー
        Exception: ファイルが必要数取得出来なかった場合
    Returns:
        str: S3に保存されたHTMLの最新2件
    """

    S3_ENDPOINT_URL = os.getenv("S3_ENDPOINT_URL")

    if S3_ENDPOINT_URL:
        s3 = boto3.resource("s3", endpoint_url=S3_ENDPOINT_URL)
    else:
        s3 = boto3.resource("s3")

    try:
        objects_iter = s3.Bucket(bucket_name).object_versions.filter(Prefix=prefix)
        obj = deque(objects_iter)
    except botocore.exceptions.ClientError as e:
        raise e

    if len(obj) <= 0:
        raise NotExistObjectException(
            "The object does not exist. bucket_name: {}, prefix: {}".format(bucket_name, prefix)
        )
    elif len(obj) == 1:
        logger.warning(
            "There weren't enough files to check diff. bucket_name: {}, prefix: {}".format(bucket_name, prefix)
        )

        # Exceptionで扱った方がPython的には良さそうだが、Step Functionで複雑に扱うよりLoggerで十分かと思われる。
        # raise NotEnoughObjectException(
        #     "There weren't enough files to check diff. bucket_name: {}, prefix: {}".format(bucket_name, prefix)
        # )

        return None, None

    incoming_obj = obj.popleft().get()
    logger.info("incoming version ID: {}".format(incoming_obj["VersionId"]))
    incoming_html = incoming_obj["Body"].read()

    current_obj = obj.popleft().get()
    logger.info("current version ID: {}".format(current_obj["VersionId"]))
    current_html = current_obj["Body"].read()

    if last_crawled_version_id != incoming_obj["VersionId"]:
        logger.warning(
            "Could not get latest crawled version. last_crawled_version_id: {}".format(last_crawled_version_id)
        )

    return current_html, incoming_html


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
