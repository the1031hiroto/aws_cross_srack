# AWS Cross Stack
## API Gateway
API GatewayとLambdaは別スタックにできない
### ローカルテスト
```
$ sam build --config-file sam_conf.toml --config-env dev
$ sam local start-api -t ".aws-sam/dev/template.yaml"
$ curl "http://127.0.0.1:3000/event_1?keywords=test_keyword&title=test_title"
```
### deploy
`sam_conf.toml`を適宜書き換える
```
$ cd lambda
$ aws ecr get-login-password --profile sample-project-2021-06-stack-iam-create-user | docker login --username AWS --password-stdin {ID}.dkr.ecr.{REGION}.amazonaws.com
$ aws s3 cp swagger.yaml s3://sample-project-2021-06/swagger/swagger.yaml
$ sam build --config-file sam_conf.toml --config-env dev
$ sam deploy --config-file sam_conf.toml --config-env dev
```
### API Key
```
$ aws cloudformation describe-stacks --stack-name sample-project-2021-06-stack-api-container --query 'Stacks[].Outputs' --profile sample-project-2021-06-stack-iam-create-user
[
    [
        {
            "OutputKey": "SampleApiKeyID",
            "OutputValue": "YYYYYYY",
            "Description": "API Key ID"
        },
        {
            "OutputKey": "SampleApiUrl",
            "OutputValue": "https://QQQQQQQQQQ.execute-api.ap-northeast-1.amazonaws.com/Prod/amazon_pa_api",
            "Description": "API Gateway endpoint URL"
        },
    ]
$ aws apigateway get-api-keys --include-values --output text --region ap-northeast-1 --query 'items[?id==`YYYYYYY`].value'
XXXXXXXXXXXXXXXXX
$ curl -H "x-api-key:XXXXXXXXXXXXXXXXX" "https://QQQQQQQQQQQ.execute-api.ap-northeast-1.amazonaws.com/Prod/amazon_pa_api"
```

### swagger.ymlをHTMLに変換
```
npm install -g bootprint
npm install -g bootprint-openapi
bootprint openapi swagger.yml ./swagger
```
