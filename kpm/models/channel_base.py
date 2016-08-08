import datetime
from kpm.exception import ChannelNotFound
import kpm.semver as semver


class ChannelBase(object):
    def __init__(self, name, package):

        self.package = package
        self.name = name
        self._iscreated = None

    def exists(self):
        return self._exists()

    def _exists(self):
        """ Check if the channel is saved already """
        raise NotImplementedError

    def save(self):
        raise NotImplementedError

    def delete(self):
        raise NotImplementedError

    @classmethod
    def all(self, package):
        """ Returns all available channels for a package """
        raise NotImplementedError

    def releases(self):
        """ Returns the list of versions """
        raise NotImplementedError

    def _add_release(self, version):
        # etcdctl put /{self.package/channels/{self.name}/version
        raise NotImplementedError

    def _remove_release(self, version):
        # etcdctl put /{self.package/channels/{self.name}/version
        raise NotImplementedError

    def current_release(self):
        versions = self.releases()
        ordered_versions = [str(x) for x in sorted(semver.versions(versions, False),
                                                   reverse=True)]
        return ordered_versions[0]

    def activate_release(self, version):
        raise NotImplementedError

    def add_release(self, version):
        if self._check_release(version) is False:
            raise ValueError("Release %s doesn't exist for package %s" % (version, self.package))
        if not self.exists():
            self.save()
        self._add_release(version)

    def remove_release(self, version):
        if self._check_release(version) is False:
            raise ValueError("Release %s doesn't exist for package %s" % (version, self.package))
        if not self.exists():
            self.save()
        self._remove_release(version)

    def _check_release(self, release_name):
        from kpm.models import Package
        version = Package.get_version(self.package, release_name)
        if version is None or str(version) != release_name:
            return False
        else:
            return True

    def _new_chan_release(self, version):
        d = {'release': version,
             'created_at': datetime.datetime.utcnow().isoformat()}
        return d

    @classmethod
    def _raise_not_found(self, package, channel=None, version=None):
        if channel is None:
            raise ChannelNotFound("No channel found for package %s" % (package),
                                  {'package': package})
        else:
            raise ChannelNotFound("channel %s doesn't exist for package %s" % (channel, package),
                                  {'channel': channel, 'package': package, 'version': version})
