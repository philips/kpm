# kpm jsonnet


## Options
```
usage: kpm jsonnet [-h] [--output {text,json}] [--namespace [NAMESPACE]]
                   [-x VARIABLES] [--shards SHARDS]
                   filepath

positional arguments:
  filepath              Fetch package from the registry

optional arguments:
  -h, --help            show this help message and exit
  --output {text,json}  output format
  --namespace [NAMESPACE]
                        kubernetes namespace
  -x VARIABLES, --variables VARIABLES
                        variables
  --shards SHARDS       Shards list/dict/count: eg. --shards=5 ;
                        --shards='[{"name": 1, "name": 2}]'
```

## Examples
