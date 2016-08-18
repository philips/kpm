import logging
import os.path
import yaml
import json
from collections import OrderedDict
import jsonpatch
import kpm.manifest_jsonnet as manifest
from kpm.kubernetes import get_endpoint
from kpm.utils import convert_utf8
from kpm.kub_base import KubBase


logger = logging.getLogger(__name__)


_mapping_tag = yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG


class KubJsonnet(KubBase):
    def __init__(self, *args, **kwargs):
        shards = kwargs.get("shards", None)
        if shards.__class__ in [str, unicode]:
            shards = json.loads(shards)
            kwargs['shards'] = shards

        super(KubJsonnet, self).__init__(*args, **kwargs)

        self.tla_codes = {"variables": self._deploy_vars}
        if shards is not None:
            self.tla_codes["shards"] = shards

        self.manifest = manifest.ManifestJsonnet(self.package, {"params": json.dumps(self.tla_codes)})

    def _create_namespaces(self):
        if self.namespace:
            ns = self.create_namespace(self.namespace)
            self._resources.insert(0, ns)

    @property
    def kubClass(self):
        return KubJsonnet

    @property
    def dependencies(self):
        if self._dependencies is None:
            self._fetch_deps()
        return self._dependencies

    def _init_resources(self):
        index = 0
        for resource in self._resources:
            index += 1
            resource["order"] = index
            if 'protected' not in resource:
                resource["protected"] = False

    def resources(self):
        if self._resources is None:
            self._resources = self.manifest.resources
            self._create_namespaces()
        return self._resources

    def prepare_resources(self, dest="/tmp", index=0):
        for resource in self.resources():
            index += 1
            path = os.path.join(dest, "%02d_%s_%s" % (index,
                                                      self.version,
                                                      resource['file']))
            f = open(path, 'w')
            f.write(yaml.safe_dump(convert_utf8(resource['value'])))
            resource['filepath'] = f.name
            f.close()
        return index

    def build(self):
        result = []
        for kub in self.dependencies:
            kubresources = OrderedDict([("package",  kub.name),
                                        ("version", kub.version),
                                        ("namespace", kub.namespace),
                                        ("resources", [])])
            for resource in kub.resources():
                self._annotate_resource(kub, resource)
                kubresources['resources'].\
                    append(OrderedDict({"file": resource['file'],
                                        "hash": resource['value']['metadata']['annotations'].get('kpm.hash', None),
                                        "protected": resource['protected'],
                                        "name": resource['name'],
                                        "kind": resource['value']['kind'].lower(),
                                        "endpoint": get_endpoint(
                                            resource['value']['kind'].lower()).
                                        format(namespace=self.namespace),
                                        "body": json.dumps(resource['value'])}))

            result.append(kubresources)
        return {"deploy": result,
                "package": {"name": self.name,
                            "version": self.version}}

    def _apply_patches(self, resources):
        for _, resource in resources.iteritems():
            if self.namespace:
                if 'namespace' in resource['value']['metadata']:
                    op = 'replace'
                else:
                    op = 'add'
                resource['patch'].append({"op": op, "path": "/metadata/namespace", "value": self.namespace})

            if len(resource['patch']):
                patch = jsonpatch.JsonPatch(resource['patch'])
                result = patch.apply(resource['value'])
                resource['value'] = result
        return resources
