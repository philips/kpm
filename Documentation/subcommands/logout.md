# kpm logout

If exists, remove the credentials stored in `~/.kpm/auth`

## Options
```
usage: kpm logout [-h] [--output {text,json}] [-H [REGISTRY_HOST]]

optional arguments:
  -h, --help            show this help message and exit
  --output {text,json}  output format
  -H [REGISTRY_HOST], --registry-host [REGISTRY_HOST]
                        registry API url
```

## Examples

```
# kpm logout
 >>> Logout complete
```

```
# kpm logout --output json
{"status": "Logout complete"}
```
