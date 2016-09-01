import os
import json
import kpm.registry
import kpm.packager
import kpm.command
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
        self.dest = options.dest
        self.path = None
        super(PullCmd, self).__init__(options)

    @classmethod
    def _add_arguments(self, parser):
        parser.add_argument('package', nargs=1, help="package-name")
        parser.add_argument("--dest", nargs="?", default="/tmp/",
                            help="directory used to extract resources")
        parser.add_argument("-v", "--version", nargs="?",
                            help="package VERSION", default=None)
        parser.add_argument("-x", "--variables",
                            help="variables", default={}, action=kpm.command.LoadVariables)
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
