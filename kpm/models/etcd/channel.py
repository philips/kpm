import etcd
from kpm.models.channel_base import ChannelBase
from kpm.models.etcd import etcd_client, etcd_listkeys, ETCD_PREFIX


class Channel(ChannelBase):
    def __init__(self, name, package):
        super(Channel, self).__init__(name, package)

    @classmethod
    def _etcdpath(self, package, name=None):
        path = ETCD_PREFIX + package + "/channels"
        if name is not None:
            path = path + "/%s" % name
        return path

    def _exists(self):
        """ Check if the channel is saved already """
        path = self._etcdpath(self.package, self.name)
        try:
            etcd_client.read(path)
        except etcd.EtcdKeyNotFound:
            return False
        return True

    def save(self):
        path = self._etcdpath(self.package, self.name)
        try:
            etcd_client.write(path, None,  dir=True)
        except etcd.EtcdAlreadyExist:
            pass

    def delete(self):
        path = self._etcdpath(self.package, self.name)
        if self.exists:
            etcd_client.delete(path, recursive=True)

    @classmethod
    def all(self, package):
        """ Returns all available channels for a package """
        path = self._etcdpath(package)
        try:
            chans = etcd_client.read(path, recursive=True)
        except etcd.EtcdKeyNotFound:
            self._raise_not_found(package)
        result = etcd_listkeys(chans, path)
        return result

    def releases(self):
        """ Returns the list of versions """
        path = self._etcdpath(self.package, self.name)
        try:
            releases = etcd_client.read(path, recursive=True)
        except etcd.EtcdKeyNotFound:
            self._raise_not_found(self.name, self.package)
        result = etcd_listkeys(releases, path)
        return result

    def _add_release(self, version):
        path = self._etcdpath(self.package, "%s/%s" % (self.name, version))
        try:
            etcd_client.write(path, self._new_chan_release(version), prevExist=False)
        except etcd.EtcdAlreadyExist:
            pass

    def _remove_release(self, version):
        path = self._etcdpath(self.package, "%s/%s" % (self.name, version))
        try:
            etcd_client.delete(path)
        except etcd.EtcdKeyNotFound:
            self._raise_not_found(self.name, self.package, version)

    def activate_release(self, version):
        raise NotImplementedError
