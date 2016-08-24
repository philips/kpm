from kpm.kub_jsonnet import KubJsonnet


def build(package, values, endpoint):
    name = package
    version = values.get('version', None)
    namespace = values.get('namespace', 'default')
    variables = values.get('variables', {})
    shards = values.get('shards', None)
    variables['namespace'] = namespace
    k = KubJsonnet(name,
                   endpoint=endpoint,
                   variables=variables,
                   namespace=namespace,
                   version=version,
                   shards=shards)
    return k


def show_file(package, filepath, endpoint):
    k = KubJsonnet(package, endpoint=endpoint)
    return k.package.file(filepath)


def tree(package, endpoint):
    k = KubJsonnet(package, endpoint=endpoint)
    return k.package.tree()
