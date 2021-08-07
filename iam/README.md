# AWS Cross Stack
## IAM
### deploy

```
$ aws cloudformation deploy \
    --template-file template.yaml \
    --stack-name sample-project-2021-06-stack-iam \
    --capabilities CAPABILITY_NAMED_IAM \
    --region ap-northeast-1 \
    --profile create-iam-user
$ aws iam create-access-key --user-name sample-project-2021-06-stack-iam-create-user
{
    "AccessKey": {
        "UserName": "sample-project-2021-06-stack-iam-create-user",
        "AccessKeyId": "YYYYYYYYYYYYYYYYYY",
        "Status": "Active",
        "SecretAccessKey": "XXXXXXXXXXXXXXXXXXXXXXX",
        "CreateDate": "2021-06-04T06:30:18+00:00"
    }
}
$ aws configure --profile sample-project-2021-06-stack-iam-create-user
AWS Access Key ID [None]: YYYYYYYYYYYYYYYYYY
AWS Secret Access Key [None]: XXXXXXXXXXXXXXXXXXXXXXX
Default region name [None]: ap-northeast-1
Default output format [None]: json
```
