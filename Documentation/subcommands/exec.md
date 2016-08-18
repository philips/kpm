# kpm exec


## Options
```
usage: kpm exec [-h] [--output {text,json}] [--namespace [NAMESPACE]]
                [-k [{deployment,rs,rc}]] [-n NAME] [-c [CONTAINER]]
                cmd [cmd ...]

positional arguments:
  cmd                   command to execute

optional arguments:
  -h, --help            show this help message and exit
  --output {text,json}  output format
  --namespace [NAMESPACE]
                        kubernetes namespace
  -k [{deployment,rs,rc}], --kind [{deployment,rs,rc}]
                        deployment, rc or rs
  -n NAME, --name NAME  resource name
  -c [CONTAINER], --container [CONTAINER]
                        container name
```

## Examples
