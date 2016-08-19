# kpm login

Authenticate an account to a registry that has enabled permissions/access control.
The command stores the credentials in `~/.kpm/auth`

## Options
```
usage: kpm login [-h] [--output {text,json}] [-H [REGISTRY_HOST]] [-s]
                 [-u [USER]] [-p [PASSWORD]] [-e [EMAIL]]

optional arguments:
  -h, --help            show this help message and exit
  --output {text,json}  output format
  -H [REGISTRY_HOST], --registry-host [REGISTRY_HOST]
                        registry API url
  -s, --signup          Create a new account and login
  -u [USER], --user [USER]
                        username
  -p [PASSWORD], --password [PASSWORD]
                        password
  -e [EMAIL], --email [EMAIL]
                        email for signup
```

See the table with [global options in general commands documentation](../commands.md#global-options).


## Examples

##### With prompt
```
# kpm login
Username: ant31
Password: **********
 >>> Login succeeded
```

##### Json output

```
# kpm login -u ant31 -p $KPM_PASSWORD --output json
{"status": "Login succeeded", "user": "ant31"}
```

##### Select the registry host

```
# kpm login -u ant31 -p $KPM_PASSWORD --output json -H https://kpm-registry.example.com
{"status": "Login succeeded", "user": "ant31"}
```
