import etcd
import re

etcd_client = etcd.Client(port=2379)

ETCD_PREFIX = "kpm/packages/"


def etcd_listkeys(key, path):
    result = []
    for child in key.children:
        m = re.match("^/%s/(.+)$" % path, child.key)
        if m is None:
            continue
        result.append(m.group(1))
    return result
