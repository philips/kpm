#!/usr/bin/env python
import hashlib
import etcd
import re

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
    data = etcd_client.read(ETCD_PREFIX + pv)
    etcd_client.write(ETCD_PREFIX + package + "/" + "releases" + "/" + version, data.value)
    etcd_client.delete(ETCD_PREFIX + pv)
    print "%s/%s" % (package, version)

for child in packages.children:
    m = re.match("^/%s(.+?)/(.+?)/releases/(.+?)$" % ETCD_PREFIX, child.key)
    if m is None:
        continue
    organization, name, version = (m.group(1), m.group(2), m.group(3))
    if len(version.split("/")) > 1:
        continue
    package = "%s/%s" % (organization, name)
    pv = "%s/%s" % (package, version)
    data = etcd_client.read(ETCD_PREFIX + package + "/releases/" + version)
    print pv
    sha = hashlib.sha256(data.value).hexdigest()
    etcd_client.write(ETCD_PREFIX + package + "/" + "digests" + "/" + sha, data.value)
    print sha
