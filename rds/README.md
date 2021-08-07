# RDSのCloudformationのテンプレート

## デプロイ
`sam_conf.toml`を適宜書き換える
### Subnet
```
$ sam build --config-file sam_conf.toml --config-env subnet
$ sam deploy --config-file sam_conf.toml --config-env subnet
```
### RDS
```
$ sam build --config-file sam_conf.toml --config-env rds
$ sam deploy --config-file sam_conf.toml --config-env rds
```

