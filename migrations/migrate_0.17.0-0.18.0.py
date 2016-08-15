#!/usr/bin/env python
import hashlib
import etcd
import re
from kpm.models.etcd.package import Package

etcd_client = etcd.Client(port=2379)
ETCD_PREFIX = "kpm/packages/"


path = ETCD_PREFIX
r = {}
packages = etcd_client.read(path, recursive=True)

for child in packages.children:
    m = re.match("^/%s(.+?)/(.+?)/(.+?)$" % ETCD_PREFIX, child.key)
    if m is None:
        continue
    organization, name, version = (m.group(1), m.group(2), m.group(3))
    if len(version.split("/")) > 1:
        continue
    package = "%s/%s" % (organization, name)
    pv = "%s/%s" % (package, version)
    data = etcd_client.read(ETCD_PREFIX + pv).value
    p = Package(package, version, data)
    p.save()
    etcd_client.delete(ETCD_PREFIX + pv)
    print "%s/%s" % (package, version)
