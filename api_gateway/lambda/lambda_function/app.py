import os
import json
import logging

logger = logging.getLogger()
level_name = os.environ.get("LOG_LEVEL")
level = logging.getLevelName(level_name)
if not isinstance(level, int):
    level = logging.INFO
logger.setLevel(level)


def lambda_handler(event, context):
    status_code = 200
    response_body = {}
    queryStringParameters = event.get("queryStringParameters", {})
    keywords = queryStringParameters.get("keywords")
    title = queryStringParameters.get("title")

    try:
        response_body = some_function(keywords, title)
    except Exception as e:
        status_code = 500
        response_body = json.dumps({"c": str(e)})

    return {
        "statusCode": status_code,
        # 'headers': {
        #     'Access-Control-Allow-Headers': 'Content-Type',
        #     'Access-Control-Allow-Origin': '*',
        #     'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        # },
        "body": response_body,
    }

def some_function(keywords, title):
    message = "hello World"
    result = {
        "keywords": keywords,
        "title": title,
        "message": message
    }
    return result
