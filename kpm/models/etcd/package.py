import etcd
import kpm.semver as semver
import re
from kpm.models.package_base import PackageModelBase
from kpm.exception import PackageAlreadyExists
from kpm.models.etcd import etcd_client, ETCD_PREFIX


class Package(PackageModelBase):
    def __init__(self, package_name, version, blob=None):
        super(Package, self).__init__(package_name, version, blob)

    @classmethod
    def _fetch(self, package, version):
        path = self._etcdkey(package, str(version))
        try:
            package_data = etcd_client.read(path)
        except etcd.EtcdKeyNotFound:
            self._raise_not_found(package, version)
        return package_data

    @classmethod
    def all_versions(self, package):
        path = ETCD_PREFIX + package + "/releases"
        try:
            r = etcd_client.read(path, recursive=True)
        except etcd.EtcdKeyNotFound:
            self._raise_not_found(package, None)

        versions = []
        for p in r.children:
            version = p.key.split("/")[-1]
            versions.append(version)
        return versions

    @classmethod
    def all(self, organization=None):
        path = ETCD_PREFIX
        r = {}
        if organization is not None:
            path += "/%s" % organization
        try:
            packages = etcd_client.read(path, recursive=True)
        except etcd.EtcdKeyNotFound:
            etcd_client.write(path, None, dir=True)

        for child in packages.children:
            m = re.match("^/%s(.+)/(.+)/releases/(.+)$" % ETCD_PREFIX, child.key)
            if m is None:
                continue
            organization, name, version = (m.group(1), m.group(2), m.group(3))
            package = "%s/%s" % (organization, name)
            if package not in r:
                r[package] = {"name": package, 'available_versions': [], 'version': None}
                r[package]['available_versions'].append(version)

        for _, v in r.iteritems():
            v['available_versions'] = [str(x) for x in sorted(semver.versions(v['available_versions'], False),
                                                              reverse=True)]
            v['version'] = v['available_versions'][0]
        return r.values()

    def _save(self, force=False):
        self._push_etcd(self.package, self.version, self.blob, force=force)

    def delete(self):
        raise NotImplementedError

    @classmethod
    def _etcdkey(self, package, version):
        return ETCD_PREFIX + "%s/releases/%s" % (package, version)

    def _push_etcd(self, package, version, data, force=False):
        path = self._etcdkey(package, version)
        try:
            etcd_client.write(path, data, prevExist=force)
        except etcd.EtcdAlreadyExist as e:
            raise PackageAlreadyExists(e.message, {"package": path})
        except etcd.EtcdKeyNotFound as e:
            etcd_client.write(path, data, prevExist=False)
