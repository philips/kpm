# kpm version

This command prints the kpm client-version and kpm-registry version

## Options
```
usage: kpm version [-h] [--output {text,json}] [-H [REGISTRY_HOST]]

optional arguments:
  -h, --help            show this help message and exit
  --output {text,json}  output format
  -H [REGISTRY_HOST], --registry-host [REGISTRY_HOST]
                        registry API url
```
## Example

```
# kpm version
Api-version: {u'kpm-api': u'0.5.10'}
Client-version: 0.20.0
```

```
# kpm version -H http://localhost:5000 --output json
{"api-version": {"kpm-api": "0.19.0"}, "client-version": "0.20.0"}
```
