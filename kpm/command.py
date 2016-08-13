#!/usr/bin/env python
import argparse
import json
import kpm
import kpm.kub
import kpm.kub_jsonnet
from kpm.auth import KpmAuth
import kpm.registry
import kpm.manifest
import kpm.deploy
from kpm.display import print_packages
from kpm.console import KubernetesExec
from kpm.utils import parse_cmdline_variables

from kpm.commands import all_commands


def install(options):
    variables = None
    if options.variables is not None:
        variables = parse_cmdline_variables(options.variables)

    kpm.deploy.deploy(options.package[0],
                      version=options.version,
                      dest=options.tmpdir,
                      namespace=options.namespace,
                      force=options.force,
                      dry=options.dry_run,
                      endpoint=options.registry_host,
                      proxy=options.api_proxy,
                      variables=variables,
                      shards=options.shards,
                      jsonnet=options.jsonnet)


def remove(options):
    kpm.deploy.delete(options.package[0],
                      version=options.version,
                      dest=options.tmpdir,
                      namespace=options.namespace,
                      dry=options.dry_run,
                      endpoint=options.registry_host,
                      proxy=options.api_proxy,
                      jsonnet=options.jsonnet)


def generate(options):
    name = options.pull[0]
    version = options.version
    namespace = options.namespace
    variables = {}
    if options.variables is not None:
        variables = parse_cmdline_variables(options.variables)

    variables['namespace'] = namespace
    if options.jsonnet is True:
        kubClass = kpm.kub_jsonnet.KubJsonnet
    else:
        kubClass = kpm.kub.Kub

    k = kubClass(name, endpoint=options.registry_host,
                 variables=variables, namespace=namespace, version=version)
    filename = "%s_%s.tar.gz" % (k.name.replace("/", "_"), k.version)
    with open(filename, 'wb') as f:
        f.write(k.build_tar("."))
    print json.dumps(k.manifest, indent=2, separators=(',', ': '))


def exec_cmd(options):
    c = KubernetesExec(options.name,
                       cmd=" ".join(options.cmd),
                       namespace=options.namespace,
                       container=options.container,
                       kind=options.kind)
    c.call()


def jsonnet(options):
    from kpm.render_jsonnet import RenderJsonnet
    r = RenderJsonnet()
    namespace = options.namespace
    variables = {}
    if options.variables is not None:
        variables = parse_cmdline_variables(options.variables)
    variables['namespace'] = namespace
    tla_codes = {"variables": variables}
    p = open(options.filepath[0]).read()
    result = r.render_jsonnet(p, tla_codes={"params": json.dumps(tla_codes)})
    print json.dumps(result)


def list_packages(options):
    r = kpm.registry.Registry(options.registry_host)
    response = r.list_packages(user=options.user, organization=options.organization)
    print_packages(response)


def logout(options):
    KpmAuth().delete_token()
    print ' >>> Logout complete'


def delete_package(options):
    r = kpm.registry.Registry(options.registry_host)
    r.delete_package(options.package[0], version=options.version)
    print "Package %s deleted" % (options.package[0])


def channel(options):
    r = kpm.registry.Registry(options.registry_host)
    package = options.package[0]
    name = options.name
    if options.create is True:
        if options.name is None:
            raise ValueError("missing channel name")
        r.create_channel(package, name)
        print ">>> Channel '%s' on '%s' created" % (name, package)
    elif options.add is None and options.remove is None:
        if name is None:
            print r.list_channels(package)
        else:
            print r.show_channel(package, name)
    else:
        if options.add is not None:
            r.create_channel_release(package, name, options.add)
            print ">>> Release '%s' added on '%s'" % (options.add, name)
        if options.remove is not None:
            r.delete_channel_release(package, name, options.remove)
            print ">>> Release '%s' removed from '%s'" % (options.remove, name)


def get_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument("--namespace",
                        help="namespace to deploy the application")
    parser.add_argument("--output", default="text",  choices=['text', 'json'],
                        help="namespace to deploy the application")

    subparsers = parser.add_subparsers(help='command help')

    for _, commandClass in all_commands.iteritems():
        commandClass.add_parser(subparsers)

    # Logout
    logout_parser = subparsers.add_parser('logout', help='logout')
    logout_parser.add_argument("-H", "--registry-host", nargs="?", default=kpm.registry.DEFAULT_REGISTRY,
                               help='registry API url')
    logout_parser.set_defaults(func=logout)

    # Install
    install_parser = subparsers.add_parser('deploy', help='deploy a package on kubernetes')
    install_parser.add_argument('package', nargs=1, help="package-name")
    install_parser.add_argument("--tmpdir", nargs="?", default="/tmp/",
                                help="directory used to extract resources")
    install_parser.add_argument("--dry-run", action='store_true', default=False,
                                help="do not create the resources on kubernetes")
    install_parser.add_argument("--namespace", nargs="?",
                                help="kubernetes namespace", default=None)
    install_parser.add_argument("--api-proxy", nargs="?",
                                help="kubectl proxy url", const="http://localhost:8001")
    install_parser.add_argument("-v", "--version", nargs="?",
                                help="package VERSION", default=None)
    install_parser.add_argument("-x", "--variables",
                                help="variables", default=None, action="append")
    install_parser.add_argument('-j', "--jsonnet", action="store_true", default=False,
                                help="Experimental Jsonnet format")
    install_parser.add_argument("--shards",
                                help="Shards list/dict/count: eg. --shards=5 ; --shards='[{\"name\": 1, \"name\": 2}]'",
                                default=None)
    install_parser.add_argument("--force", action='store_true', default=False,
                                help="force upgrade, delete and recreate resources")
    install_parser.add_argument("-H", "--registry-host", nargs="?", default=kpm.registry.DEFAULT_REGISTRY,
                                help='registry API url')
    install_parser.set_defaults(func=install)

    # remove
    remove_parser = subparsers.add_parser('remove', help='remove a package from kubernetes')
    remove_parser.add_argument('package', nargs=1, help="package-name")
    remove_parser.add_argument("--tmpdir", nargs="?", default="/tmp/",
                               help="directory used to extract resources")
    remove_parser.add_argument("--dry-run", action='store_true', default=False,
                               help="Does not delete the resources on kubernetes")
    remove_parser.add_argument("--namespace", nargs="?",
                               help="kubernetes namespace", default=None)
    remove_parser.add_argument("--api-proxy", nargs="?",
                               help="kubectl proxy url", const="http://localhost:8001")
    remove_parser.add_argument('-j', "--jsonnet", action="store_true",
                               default=False, help="Experimental Jsonnet format")
    remove_parser.add_argument("-v", "--version", nargs="?",
                               help="package VERSION to delete", default=None)

    remove_parser.add_argument("-H", "--registry-host", nargs="?", default=kpm.registry.DEFAULT_REGISTRY,
                               help='registry API url')
    remove_parser.set_defaults(func=remove)

    # list
    list_parser = subparsers.add_parser('list', help='list packages')
    list_parser.add_argument("-u", "--user", nargs="?", default=None,
                             help="list packages owned by USER")
    list_parser.add_argument("-o", "--organization", nargs="?", default=None,
                             help="list ORGANIZATION packages")
    list_parser.add_argument("-H", "--registry-host", nargs="?", default=kpm.registry.DEFAULT_REGISTRY,
                             help='registry API url')

    list_parser.set_defaults(func=list_packages)

    # channel
    channel_parser = subparsers.add_parser('channel', help='channel packages')
    channel_parser.add_argument("-n", "--name", nargs="?", default=None,
                                help="channel name")
    channel_parser.add_argument("--add", nargs="?", default=None,
                                help="Add a version to the channel")
    channel_parser.add_argument("--create", default=False, action='store_true',
                                help="Create the channel")
    channel_parser.add_argument("--remove", nargs="?", default=None,
                                help="Remove a version to the channel")
    channel_parser.add_argument("-H", "--registry-host", nargs="?", default=kpm.registry.DEFAULT_REGISTRY,
                                help='registry API url')
    channel_parser.add_argument('package', nargs=1, help="package-name")

    channel_parser.set_defaults(func=channel)

    #  DELETE-PACKAGE
    delete_parser = subparsers.add_parser('delete-package', help='delete package from the registry')
    delete_parser.add_argument('package', nargs=1, help="package-name")
    delete_parser.add_argument("-H", "--registry-host", nargs="?", default=kpm.registry.DEFAULT_REGISTRY,
                               help='registry API url')
    delete_parser.add_argument("-v", "--version", nargs="?", default=None,
                               help="package version")

    delete_parser.set_defaults(func=delete_package)

    #  EXEC
    exec_parser = subparsers.add_parser('exec', help='exec a command in pod from the RC or RS name.\
    It executes the command on the first matching pod')
    exec_parser.add_argument('cmd', nargs='+', help="command to execute")
    exec_parser.add_argument("--namespace", nargs="?",
                             help="kubernetes namespace", default='default')

    exec_parser.add_argument('-k', '--kind', choices=['deployment', 'rs', 'rc'], nargs="?",
                             help="deployment, rc or rs", default='rc')
    exec_parser.add_argument('-n', '--name', help="resource name", default='rs')
    exec_parser.add_argument('-c', '--container', nargs='?', help="container name", default=None)

    exec_parser.set_defaults(func=exec_cmd)

    #  Generate
    generate_parser = subparsers.add_parser('generate', help='generate a command in pod from the RC or RS name.\
    It generateutes the command on the first matching pod')
    generate_parser.add_argument("--namespace", nargs="?",
                                 help="kubernetes namespace", default='default')
    generate_parser.add_argument("-x", "--variables",
                                 help="variables", default=None, action="append")
    generate_parser.add_argument('-p', "--pull", nargs=1, help="Fetch package from the registry")
    generate_parser.add_argument('-j', "--jsonnet", action="store_true", default=False, help="Experimental Jsonnet")
    generate_parser.add_argument("-H", "--registry-host", nargs="?", default=kpm.registry.DEFAULT_REGISTRY,
                                 help='registry API url')
    generate_parser.add_argument("-v", "--version", nargs="?", default=None,
                                 help="package version")

    generate_parser.set_defaults(func=generate)

    # Jsonnet
    jsonnet_parser = subparsers.add_parser('jsonnet', help='jsonnet a command in pod from the RC or RS name.\
    It jsonnetutes the command on the first matching pod')
    jsonnet_parser.add_argument("--namespace", nargs="?",
                                help="kubernetes namespace", default='default')
    jsonnet_parser.add_argument("-x", "--variables",
                                help="variables", default=None, action="append")
    jsonnet_parser.add_argument("--shards",
                                help="Shards list/dict/count: eg. --shards=5 ; --shards='[{\"name\": 1, \"name\": 2}]'",
                                default=None)

    jsonnet_parser.add_argument('filepath', nargs=1, help="Fetch package from the registry")

    jsonnet_parser.set_defaults(func=jsonnet)

    return parser


def cli():
    parser = get_parser()
    args = parser.parse_args()
    try:
        args.func(args)
    except (argparse.ArgumentTypeError, argparse.ArgumentError) as e:
        parser.error(e.message)
