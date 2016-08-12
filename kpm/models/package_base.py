import semantic_version
from kpm.semver import last_version, select_version
from kpm.exception import (InvalidVersion,
                           PackageVersionNotFound,
                           PackageNotFound)


class PackageModelBase(object):
    def __init__(self, package_name, version=None, blob=None):
        self.package = package_name
        self.organization, self.name = package_name.split("/")
        self.version = version
        self._blob = blob

    @property
    def blob(self):
        return self._blob

    @blob.setter
    def blob(self, value):
        self._blob = value

    @classmethod
    def check_version(self, version):
        try:
            semantic_version.Version(version)
        except ValueError as e:
            raise InvalidVersion(e.message, {"version": version})
        return None

    @classmethod
    def get(self, package, version='latest'):
        """
        package: string following "organization/package_name" format
        version: version query. If None return latest version

        returns: (package blob(targz) encoded in base64, version)
        """
        p = self(package, version)
        p.pull(version)
        return p

    @classmethod
    def get_version(self, package, version_query, stable=False):
        versions = self.all_versions(package)
        if version_query is None or version_query == 'latest':
            return last_version(versions, stable)
        else:
            try:
                return select_version(versions, str(version_query), stable)
            except ValueError as e:
                raise InvalidVersion(e.message, {"version": version_query})

    def pull(self, version_query=None):
        if version_query is None:
            version_query = self.version
        package = self.package
        version = self.get_version(package, version_query)
        if version is None:
            raise PackageVersionNotFound("No version match '%s' for package '%s'" % (version_query, package),
                                         {"package": package, "version_query": version_query})

        self._blob = self._fetch(package, version)
        return self

    def save(self, force=False):
        self.check_version(self.version)
        self._save(force)

    def versions(self):
        return self.all_versions(self.package)

    @classmethod
    def _raise_not_found(self, package, version=None):
        raise PackageNotFound("package %s doesn't exist" % package,
                              {'package': package, 'version': version})

    @classmethod
    def all(self, organization=None):
        raise NotImplementedError

    @classmethod
    def _fetch(self, package, version):
        raise NotImplementedError

    def _save(self, force=False):
        raise NotImplementedError

    def delete(self):
        raise NotImplementedError

    @classmethod
    def all_versions(self, package):
        raise NotImplementedError
