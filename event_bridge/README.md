# AWS Cross Stack
## Event Bridge
### deploy
```
cd event_bridge
sam build --config-file sam_conf_events.toml --config-env dev
sam deploy --config-file sam_conf_events.toml --config-env dev
```
