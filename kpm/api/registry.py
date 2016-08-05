import re
import yaml
import json
from base64 import b64decode
from flask import jsonify, request, Blueprint, current_app
import semantic_version
from kpm.api.app import getvalues
from kpm.packager import Package
import kpm.semver as semver
from kpm.semver import last_version, select_version
from kpm.api.exception import (ApiException,
                               InvalidUsage,
                               InvalidVersion,
                               PackageAlreadyExists,
                               PackageNotFound,
                               PackageVersionNotFound)
import kpm.api.models.etcd_storage as models

registry_app = Blueprint('registry', __name__,)




@registry_app.errorhandler(etcd.EtcdKeyNotFound)
def render_etcdkeyerror(error):
    package = error.payload['cause']
    return render_error(PackageNotFound("Package not found: %s" % package, {"package": package}))


@registry_app.errorhandler(PackageAlreadyExists)
@registry_app.errorhandler(InvalidVersion)
@registry_app.errorhandler(PackageNotFound)
@registry_app.errorhandler(PackageVersionNotFound)
@registry_app.errorhandler(ApiException)
@registry_app.errorhandler(InvalidUsage)
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
        resp = current_app.make_response(b64decode(packagemodel.blob))
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
    package_data = packagemodel.blob
    p = Package(b64decode(package_data))
    manifest = yaml.load(p.manifest)
    stable = False
    if 'stable' in values and values['stable'] == 'true':
        stable = True

    response = {"manifest": manifest,
                "version": manifest['package']['version'],
                "name":  package,
                "available_versions": [str(x) for x in sorted(semver.versions(packagemodel.versions(), stable),
                                                              reverse=True)]}
    if 'pull' in values and values['pull'] == 'true':
        response['kub'] = package_data
    return jsonify(response)


@registry_app.route("/api/v1/packages/<path:package>", methods=['DELETE'], strict_slashes=False)
def delete_package(package):
    values = getvalues()
    packagemodel = get_package(package, values)
    packagemodel.delete()
    return jsonify({"status": "delete", "packge": packagemodel.package, "version": packagemodel.version})
