# AWS Cross Stack
## Step Functions
### deploy
```
cd statemachine
sam build --config-file sam_conf_statemachine.toml --config-env dev
sam deploy --config-file sam_conf_statemachine.toml --config-env dev
```