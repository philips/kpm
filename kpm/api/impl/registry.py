import logging
import kpm.semver as semver
import kpm.models as models


logger = logging.getLogger(__name__)


def get_package(package, version_query='latest'):
    # if version is None; Find latest version
    p = models.Package.get(package, version_query)
    return p


def pull(package, version='latest'):
    logger.info("lpull %s", package)
    packagemodel = get_package(package, version)
    resp = {"package": package,
            "blob": packagemodel.packager.blob,
            "version": packagemodel.version,
            "filename": "%s_%s.tar.gz" % (packagemodel.package.replace("/", "_"), packagemodel.version)}
    return resp


def push(package, version, blob, force=False):
    p = models.Package(package, version, blob)
    p.save(force=force)
    return {"status": "ok"}


def list_packages(organization=None):
    resp = models.Package.all(organization)
    return resp


def show_package(package, version="latest", stable=False, pullmode=False):
    packagemodel = get_package(package, version)
    p = packagemodel.packager
    manifest = p.manifest
    response = {"manifest": manifest,
                "version": packagemodel.version,
                "name":  package,
                "created_at": packagemodel.created_at,
                "channels": models.Channel.all(package).values(),
                "available_versions": [str(x) for x in sorted(semver.versions(packagemodel.versions(), stable),
                                                              reverse=True)]}
    if pullmode:
        response['kub'] = p.b64blob
    return response


# CHANNELS
def list_channels(package):
    channels = models.Channel.all(package).values()
    return channels


def show_channel(package, name):
    c = models.Channel(name, package)
    return c.to_dict()


def add_channel_release(package, name, release):
    channel = models.Channel(name, package)
    channel.add_release(release)
    return channel.to_dict()


def delete_channel_release(package, name, release):
    channel = models.Channel(name, package)
    channel.remove_release(release)
    return channel.to_dict()


def create_channel(package, name):
    channel = models.Channel(name, package)
    channel.save()
    return channel.to_dict()


def delete_channel(package, name):
    channel = models.Channel(name, package)
    channel.delete()
    return {"channel": channel.name, "package": package, "action": 'delete'}


def delete_package(package, version="latest"):
    packagemodel = get_package(package, version)
    models.Package.delete(packagemodel.package, packagemodel.version)
    return {"status": "delete", "package": packagemodel.package, "version": packagemodel.version}
