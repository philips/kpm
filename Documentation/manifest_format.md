# Manifest formats

kpm registry will be able to store and manage multiple package format from different providers.
It also propose its own format to package kubernetes applications.

## Jsonnet or Yaml

A package is composed at least by a manifest file and often resources in the `/templates` directory.
The manifest file can be write either with yaml or jsonnet.
Behind the scene kpm processes only jsonnet, the yaml manifest is converted to jsonnet.

Yaml looks more familiar but it allows less pattern.
We recommend to use jsonnet for more complex usecases, including:

 - Dynamic dependencies
 - Dynamic resources
 - Compose variables and use/reference any elements in themanifest
 - Split large manifest in multiple files with 'import'.
 - Custom function
 - Loops/Conditions (lamda complete)
 - Multiple template renderer (jsonnet/jinja2)
 - Lint and debug package with jsonnet stacktrace
 - Dependency vendoring


### Package directory structure
A package is composed of a `templates` directory and a `manifest.yaml` or `manifest.jsonnet`.
```
.
├── manifest.yaml
└── templates
    ├── heapster-rc.yaml
    └── heapster-svc.yaml
```
Optionaly, it's possible to add a `README.md` and a `LICENSE`.

#### Templates

The `templates` directory contains the kubernetes resources to deploy.

It accepts every kind of resources (deployments,secrets,pods,svc, confimap...).

Resources can be templated with Jinja2 or jsonnet.

-> We recommend to parametrize only values that should be overrided.
Having a very light templated resources improve readability and quickly point to users which values are
important to look at and change. User can use 'patch' to add their custom values.


##### Template subdirectories
Templates can be organizied in subdirectories
```
├── manifest.yaml
└── templates
    ├── api
	|    ├── api-rc.yaml
    |    └── api-svc.yaml
    └── worker
	     └── worker-rc.yaml
```

### Yaml Manifest
The `manifest.yaml` contains the following keys:

- package: metadata around the package and the packager
- variables: map jinja2 variables to default value
- resources: the list of resources, `file` refers to a filename inside the 'template' directory
- shards: see [shards-doc.md](#shards.md)
- deploy: list the dependencies, a special keyword `$self` indicate to deploy current package.


```yaml
package:
  name: ant31/heapster
  author: "Antoine Legrand <2t.antoine@gmail.com>"
  version: 0.18.2
  description: Kubernetes data
  license: MIT

variables:
  namespace: kube-system
  replicas: 1
  image: "gcr.io/google_containers/heapster:v0.18.2"
  svc_type: "NodePort"

resources:
  - file: heapster-svc.yaml
    name: heapster
    type: svc

  - file: heapster-rc.yaml
    name: heapster
    type: rc

shards: []

deploy:
  - name: $self
```


#### Package

The `package` part list the meta-data of the package.
The two important fields are `name` and `version`, others are informative only.

name:
```yaml
package:
# identify the package
# composed of two part: "namespace/name",
# format: "[a-z0-9-_]{3,63}/[a-z0-9-_]{3,63}
  name: example/package1

# Maintainer, no format
  author: Foo Bar <foo.bar@example.com>

# Short description of the package/application
  description: Great application of the organization example

# License of the package
  license: Liense

# Version of the package
# format: semver 2.0
  version: 1.4.0-alpha.1
```


#### Variables

Default values of your templates lives under `variables`.
Templates are resolved twice then a variable can reference an another variable

```yaml
variables:
	image: registry/myapp-container:v1.4.0-aplha.1
	database_url: db.{{namespace}}.svc.cluster.local    # use variables inside other variable's value
	data_volme:   # can use hash/array too
	  - name: data
	    emptyDir: {medium: ""}

```


#### Resources

The resources list, list the kubernetes resources to manage.
Resources files live in the directory `templates`.

##### Why not automaticaly create all resources found in `/templates`?

Most of the time it's useful to add some metadata around the resource itself and sort the deployment.
Listing manully each resources, give the granularity necessary to get features like
 - dynamic resources: conditional deployment of the resource (eg: deploy the ingress or not)
 - protection: never replace/update/delete the resource
 - override variables: set differents default variables for the selected resources only
 - re-use a same template: a similar template can be use to create different resources
 - enable petset: create multiple variation of a same resource

Being able to trigger/apply special setting/behavior per resource is key.
More features to come.


###### Fields

- `file: path_to_the_template.yaml`: --> relative to 'templates/'
- `name: name-of-the-resouce`: add/replace the value in '/metadata/name' of the manifest
- `type: configmap`: the resource type (see [kubectl-types](http://kubernetes.io/docs/user-guide/kubectl-overview/#resource-types)
- `protected: true`: [optional] Forbid kpm to replace/update the resource, add annotation to it
- `shards: 3`: [optional] Indicate the number of variation wanted for the resource. Allowed value types: boolean/string/integer

###### example

```yaml
resources:
  - file: etcd-certificate-secret.yaml
	protected: true
	type: secret
	name: etcd

  - file: etcd-member-dp.yaml
    name: etcd
    type: deployment
    sharded: yes

  - file: etcd-member-svc.yaml
    name: etcd
    type: svc
    sharded: yes

  - file: etcd-svc.yaml
    name: etcd
    type: svc

```

#### Deploy

The deploy section is the so-called 'dependencies'.
It lists the external package to deploy, they are deployed in order.
The default variables and shards of a dependency can be overrided.
A specific version can be pinned.

##### example
logstash:

```yaml
---
deploy:
    # deploy the current package (logstash) resources
  - name: $self

	# deploy elasticsearch version 2.3.1
  - name: elastic/elasticsearch
	version: 2.3.1

	# deploy kibana version >=2, overide default variable
  - name: elastic/kibana
	version:>=2
	variables:
      elastic_host: "elasticsearch.{{namespace}}.cluster.local"
```

#### Shards
