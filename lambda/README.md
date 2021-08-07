# AWS Cross Stack

## Lambda

### build

ビルド内容は`template.yaml`に記載する。

`$ sam build`

pythonがない場合
`$ brew install python@3.7`
`$ ln -sf /usr/local/opt/python@3.7/bin/python3.7 /usr/local/bin/`

### ローカル実行

サンプルペイロード[コマンド](https://docs.aws.amazon.com/ja_jp/serverless-application-model/latest/developerguide/sam-cli-command-reference-sam-local-generate-event.html)で作成

`$ sam local generate-event sqs receive-message`

localstack と同じネットワークを指定して s3 にアクセスする。

#### 1回限りの呼び出しを実行

invoke コマンドは Lambda 関数を直接呼び出し、指定した入力イベントペイロードを渡す。

`sam local invoke CrawlerFunction -e tests/events/event_crawler.json --docker-network sam-app_default`
`sam local invoke CheckDiffFunction -e tests/events/event_check_diff.json --docker-network sam-app_default`
`sam local invoke SaveToRdsFunction -e tests/events/event_save_to_rds.json --docker-network sam-app_default`

#### API をローカルでホストして呼び出し

`$ sam local start-lambda --docker-network sam-app_default --debug`

`$ aws lambda invoke --function-name CrawlerFunction --endpoint-url "http://127.0.0.1:3001" --payload file://tests/events/event_crawler.json response.json`

### Docker でテスト

`lambci/lambda:build-python3.8`イメージを使用して Lambda 環境でテストする。

`$ docker-compose up --build python`

### Lambdaコンテナ運用
#### Lambda単体の場合
[ECRへDocker イメージのプッシュ](https://docs.aws.amazon.com/ja_jp/AmazonECR/latest/userguide/docker-push-ecr-image.html)
ECRにレポジトリ作成すると『プッシュコマンドの表示』があるのでそれを見るのが一番簡単

コマンド例
```
aws ecr get-login-password --region {REGION} | docker login --username AWS --password-stdin {ID}.dkr.ecr.{REGION}.amazonaws.com # 認証
docker build -t test . # `test`って名前のイメージをビルド
docker tag test:latest {ID}.dkr.ecr.{REGION}.amazonaws.com/test:latest # AWS リポジトリにイメージをプッシュできるように、イメージにタグを付け
docker push {ID}.dkr.ecr.{REGION}.amazonaws.com/test:latest # AWS リポジトリにイメージをプッシュ
```

#### SAMの場合
ECRにレポジトリ作成を作成して、ローカルで認証してからデプロイすれば自動でやってくれる

コマンド例
```
aws ecr get-login-password --region {REGION} | docker login --username AWS --password-stdin {ID}.dkr.ecr.{REGION}.amazonaws.com
sam deploy
```

デプロイ情報は`samconfig.toml`に記載、新規の場合は`sam deploy --guided`で設定していく

### Deploy
※ 前提：ECRのレポジトリとS3のバケットが存在する
```
aws ecr get-login-password --profile sample-project-stack-iam-create-user | docker login --username AWS --password-stdin 117232438179.dkr.ecr.ap-southeast-1.amazonaws.com
cd lambda
sam build --config-file sam_conf_lambda.toml --config-env dev
sam deploy --config-file sam_conf_lambda.toml --config-env dev
```
