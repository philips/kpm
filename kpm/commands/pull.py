import os
import json
import kpm.registry
import kpm.packager
from kpm.manifest_jsonnet import ManifestJsonnet
from kpm.commands.command_base import CommandBase


class PullCmd(CommandBase):
    name = 'pull'
    help_message = "download a package and extract it"

    def __init__(self, options):
        self.output = options.output
        self.package = options.package[0]
        self.registry_host = options.registry_host
        self.version = options.version
        self.dest = options.tmpdir
        self.path = None
        super(PullCmd, self).__init__(options)

    @classmethod
    def _add_arguments(self, parser):
        parser.add_argument('package', nargs=1, help="package-name")
        parser.add_argument("--tmpdir", nargs="?", default="/tmp/",
                            help="directory used to extract resources")
        parser.add_argument("--dry-run", action='store_true', default=False,
                            help="do not create the resources on kubernetes")
        parser.add_argument("--namespace", nargs="?",
                            help="kubernetes namespace", default=None)
        parser.add_argument("--api-proxy", nargs="?",
                            help="kubectl proxy url", const="http://localhost:8001")
        parser.add_argument("-v", "--version", nargs="?",
                            help="package VERSION", default=None)
        parser.add_argument("-x", "--variables",
                            help="variables", default=None, action="append")
        parser.add_argument("--shards",
                            help="Shards list/dict/count: eg. --shards=5 ; --shards='[{\"name\": 1, \"name\": 2}]'",
                            default=None)
        parser.add_argument("--force", action='store_true', default=False,
                            help="force upgrade, delete and recreate resources")
        parser.add_argument("-H", "--registry-host", nargs="?", default=kpm.registry.DEFAULT_REGISTRY,
                            help='registry API url')

    def _call(self):
        r = kpm.registry.Registry(self.registry_host)
        result = r.pull(self.package, version=self.version)
        p = kpm.packager.Package(result, b64_encoded=False)
        self.path = os.path.join(self.dest, ManifestJsonnet(p).package_name())
        p.extract(self.path)

    def _render_json(self):
        print json.dumps({"pull": self.package,
                          "extrated": self.path})

    def _render_console(self):
        print "Pull package: %s... \nExtract to %s" % (self.package, self.path)
