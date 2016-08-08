import etcd

etcd_client = etcd.Client(port=2379)

ETCD_PREFIX = "kpm/packages/"
