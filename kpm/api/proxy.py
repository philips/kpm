from flask import jsonify, Blueprint
from kpm.api.authorization import check_access
import kpm.api.builder
import kpm.api.registry

proxy_app = Blueprint('proxy', __name__,)


@proxy_app.route("/api/v1/packages/<path:package>/generate", methods=['GET'], strict_slashes=False)
@check_access('read')
def generate_package(package):
    return kpm.api.builder.build(package)


@proxy_app.route("/api/v1/packages/<path:package>/pull", methods=['GET'], strict_slashes=False)
@check_access('read')
def pull_package(package):
    return kpm.api.registry.pull(package)


@proxy_app.route("/api/v1/packages/count", methods=['GET'], strict_slashes=False)
def package_count(package):
    return jsonify({})


# @TODO filter privates
@proxy_app.route("/api/v1/packages", methods=['GET'], strict_slashes=False)
def packages():
    return kpm.api.registry.list_packages()


@proxy_app.route("/api/v1/packages/<path:package>", methods=['GET'], strict_slashes=False)
@check_access('read')
def package(package):
    return kpm.api.registry.show_package(package)


@proxy_app.route("/api/v1/packages/<path:package>", methods=['POST'], strict_slashes=False)
@proxy_app.route("/api/v1/packages", methods=['POST'], strict_slashes=False)
@check_access('write')
def push_package(package):
    return kpm.api.registry.push(package)


@proxy_app.route("/api/v1/packages/<path:package>/tree", methods=['GET'], strict_slashes=False)
@check_access('read')
def package_tree(package):
    return kpm.api.builder.tree(package)


@proxy_app.route("/api/v1/packages/<path:package>/file/<path:filepath>", methods=['GET'], strict_slashes=False)
@check_access('read')
def show_file(package, filepath):
    return kpm.api.builder.show_file(package, filepath)
