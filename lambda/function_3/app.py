import os
import logging
import pymysql
import datetime

logger = logging.getLogger()
level_name = os.environ.get("LOG_LEVEL")
level = logging.getLevelName(level_name)
if not isinstance(level, int):
    level = logging.INFO
logger.setLevel(level)

rds_host = os.environ.get("DB_HOST")
port = int(os.environ.get("DB_PORT"))
db_name = os.environ.get("DB_NAME")
db_user_name = os.environ.get("DB_USER_NAME")
db_password = os.environ.get("DB_PASSWORD")
db_connect_timeout = int(os.environ.get("DB_CONNECT_TIMEOUT"))


def lambda_handler(event, context):
    """差分確認結果をRDSに保存
    Args:
        event (obj): Lambdaが受け取るイベント
        context (obj): コンテキスト情報
    Raises:
        e: MySQLError
    Returns:
        obj: [description]
    """
    logger.info("event: {}".format(event))

    crawl_url_id = event["crawl_url_id"]
    is_changed = event["is_changed"]
    diff_version_id = event["diff_version_id"]
    last_crawled_version_id = event["last_crawled_version_id"]
    state_machine_execution_id = event["state_machine_execution_id"]
    now_utc = datetime.datetime.now(datetime.timezone.utc).strftime("%Y/%m/%d %H:%M:%S")

    crawl_histories_query = "INSERT INTO crawl_histories (crawl_url_id, is_changed, diff_version_id, crawled_version_id, state_machine_execution_id, created_at, updated_at) VALUES ({0},{1},'{2}','{3}','{4}','{5}','{5}')".format(
        crawl_url_id, is_changed, diff_version_id, last_crawled_version_id, state_machine_execution_id, now_utc
    )

    try:
        conn = pymysql.connect(
            host=rds_host,
            port=port,
            user=db_user_name,
            passwd=db_password,
            db=db_name,
            connect_timeout=db_connect_timeout,
        )
    except pymysql.MySQLError as e:
        logger.error("ERROR: Unexpected error: Could not connect to MySQL instance.")
        logger.error(e)
        raise e

    with conn.cursor() as cur:
        cur.execute(crawl_histories_query)
        cur.execute(crawl_urls_query)

    try:
        conn.commit()
    except pymysql.MySQLError as e:
        logger.error(
            "ERROR: Unexpected error: Could not save data. db_name: {}, crawl_url_id: {}".format(db_name, crawl_url_id)
        )
        logger.error(e)
        raise e
    finally:
        conn.close()

    return_body = {
        "original_input": event.get("original_input"),
        "rds_host": rds_host,
        "db_name": db_name,
        "crawl_url_id": crawl_url_id,
        "crawl_histories_query": crawl_histories_query,
        "crawl_urls_query": crawl_urls_query,
    }

    logger.info("return: {}".format(return_body))

    return return_body
