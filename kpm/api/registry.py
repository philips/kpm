import yaml
import json
from flask import jsonify, request, Blueprint, current_app
from kpm.api.app import getvalues
import kpm.semver as semver

from kpm.exception import (KpmException,
                           InvalidUsage,
                           InvalidVersion,
                           PackageAlreadyExists,
                           ChannelAlreadyExists,
                           PackageNotFound,
                           ChannelNotFound,
                           PackageVersionNotFound)

import kpm.models as models
import etcd

registry_app = Blueprint('registry', __name__,)


@registry_app.errorhandler(etcd.EtcdKeyNotFound)
def render_etcdkeyerror(error):
    package = error.payload['cause']
    return render_error(PackageNotFound("Package not found: %s" % package, {"package": package}))


@registry_app.errorhandler(PackageAlreadyExists)
@registry_app.errorhandler(ChannelAlreadyExists)
@registry_app.errorhandler(InvalidVersion)
@registry_app.errorhandler(PackageNotFound)
@registry_app.errorhandler(PackageVersionNotFound)
@registry_app.errorhandler(KpmException)
@registry_app.errorhandler(InvalidUsage)
@registry_app.errorhandler(ChannelNotFound)
def render_error(error):
    response = jsonify({"error": error.to_dict()})
    response.status_code = error.status_code
    return response


@registry_app.route("/test_error")
def test_error():
    raise InvalidUsage("error message", {"path": request.path})


def get_package(package, values):
    # if version is None; Find latest version
    version_query = values.get("version", 'latest')
    p = models.Package.get(package, version_query)
    return p


@registry_app.route("/api/v1/packages/<path:package>/pull", methods=['GET'], strict_slashes=False)
def pull(package):
    current_app.logger.info("pull %s", package)
    values = getvalues()
    packagemodel = get_package(package, values)
    if 'format' in values and values['format'] == 'json':
        resp = jsonify({"package": package, "kub": packagemodel.blob})
    else:
        resp = current_app.make_response(packagemodel.packager.blob)
        resp.headers['Content-Disposition'] = 'filename="%s_%s.tar.gz"' % (packagemodel.package.replace("/", "_"),
                                                                           packagemodel.version)
        resp.mimetype = 'application/x-gzip'
    return resp


@registry_app.route("/api/v1/packages/<path:package>", methods=['POST'], strict_slashes=False)
@registry_app.route("/api/v1/packages", methods=['POST'], strict_slashes=False)
def push(package=None):
    values = getvalues()
    blob = values['blob']
    package = values['package']
    version = values['version']
    force = False
    if 'force' in values:
        force = 'true' == values['force']
    p = models.Package(package, version, blob)
    p.save(force=force)
    return jsonify({"status": "ok"})


@registry_app.route("/api/v1/packages", methods=['GET'], strict_slashes=False)
def list_packages():
    values = getvalues()
    r = models.Package.all(values.get('organization', None))
    resp = current_app.make_response(json.dumps(r))
    resp.mimetype = 'application/json'
    return resp


@registry_app.route("/api/v1/packages/<path:package>", methods=['GET'], strict_slashes=False)
def show_package(package):
    values = getvalues()
    packagemodel = get_package(package, values)
    p = packagemodel.packager
    manifest = p.manifest
    stable = False
    if 'stable' in values and values['stable'] == 'true':
        stable = True

    response = {"manifest": manifest,
                "version": packagemodel.version,
                "name":  package,
                "created_at": packagemodel.created_at,
                "channels": models.Channel.all(package).values(),
                "available_versions": [str(x) for x in sorted(semver.versions(packagemodel.versions(), stable),
                                                              reverse=True)]}
    if 'pull' in values and values['pull'] == 'true':
        response['kub'] = p.b64blob
    return jsonify(response)


# CHANNELS
@registry_app.route("/api/v1/packages/<path:package>/channels", methods=['GET'], strict_slashes=False)
def list_channels(package):
    channels = models.Channel.all(package).values()
    return jsonify({"channels": channels, 'package': package})


@registry_app.route("/api/v1/packages/<path:package>/channels/<string:channel>", methods=['GET'], strict_slashes=False)
def show_channel(package, channel):
    c = models.Channel(channel, package)
    r = c.releases()
    channels = [{"releases": r, "channel": channel, "current": c.current_release(r)}]
    return jsonify({"channels": channels, 'package': package})


@registry_app.route("/api/v1/packages/<path:package>/channels/<string:name>/<string:release>",
                    methods=['POST'], strict_slashes=False)
def add_channel_release(package, name, release):
    channel = models.Channel(name, package)
    r = channel.add_release(release)
    return jsonify({"channel": channel.name, "package": package,
                    "release": release, "created_at": r['created_at'], 'action': 'create'})


@registry_app.route("/api/v1/packages/<path:package>/channels/<string:name>/<string:release>",
                    methods=['DELETE'], strict_slashes=False)
def delete_channel_release(package, name, release):
    channel = models.Channel(name, package)
    return jsonify({"channel": channel.name, "package": package, "release": release, "action": 'delete'})


@registry_app.route("/api/v1/packages/<path:package>/channels/<string:name>",
                    methods=['POST'], strict_slashes=False)
def create_channel(package, name):
    channel = models.Channel(name, package)
    channel.save()
    return show_channel(package, name)


@registry_app.route("/api/v1/packages/<path:package>/channels/<string:name>",
                    methods=['DELETE'], strict_slashes=False)
def delete_channel(package, name):
    channel = models.Channel(name, package)
    channel.delete()
    return jsonify({"channel": channel.name, "package": package, "action": 'delete'})


@registry_app.route("/api/v1/packages/<string:orga>/<string:pname>", methods=['DELETE'], strict_slashes=False)
def delete_package(orga, pname):
    package = "%s/%s" % (orga, pname)
    values = getvalues()
    packagemodel = get_package(package, values)
    models.Package.delete(packagemodel.package, packagemodel.version)
    return jsonify({"status": "delete", "package": packagemodel.package, "version": packagemodel.version})
