# kpm deploy


## Options
```
usage: kpm deploy [-h] [--output {text,json}] [--tmpdir [TMPDIR]] [--dry-run]
                  [--namespace [NAMESPACE]] [--api-proxy [API_PROXY]]
                  [-v [VERSION]] [-x VARIABLES] [--shards SHARDS] [--force]
                  [-H [REGISTRY_HOST]]
                  package

positional arguments:
  package               package-name

optional arguments:
  -h, --help            show this help message and exit
  --output {text,json}  output format
  --tmpdir [TMPDIR]     directory used to extract resources
  --dry-run             do not create the resources on kubernetes
  --namespace [NAMESPACE]
                        kubernetes namespace
  --api-proxy [API_PROXY]
                        kubectl proxy url
  -v [VERSION], --version [VERSION]
                        package VERSION
  -x VARIABLES, --variables VARIABLES
                        variables
  --shards SHARDS       Shards list/dict/count: eg. --shards=5 ;
                        --shards='[{"name": 1, "name": 2}]'
  --force               force upgrade, delete and recreate resources
  -H [REGISTRY_HOST], --registry-host [REGISTRY_HOST]
                        registry API url
```

## Examples
