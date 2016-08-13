import os
import json
import kpm.registry
import kpm.packager
import kpm.manifest
import kpm.manifest_jsonnet
from kpm.commands.command_base import CommandBase


class PullCmd(CommandBase):
    name = 'pull'
    help_message = "download a package and extract it"

    def __init__(self, options):
        self.output = options.output
        self.package = options.package[0]
        self.registry_host = options.registry_host
        self.version = options.version
        self.dest = options.directory
        self.isjsonnet = options.jsonnet
        self.path = None
        super(PullCmd, self).__init__(options)

    @classmethod
    def _add_arguments(self, parser):
        parser.add_argument('package', nargs=1, help="package-name")
        parser.add_argument("-H", "--registry-host", nargs="?", default=kpm.registry.DEFAULT_REGISTRY,
                            help='registry API url')
        parser.add_argument("--directory", nargs="?", default=".",
                            help="destionation directory")
        parser.add_argument("-v", "--version", nargs="?", default=None,
                            help="package version")
        parser.add_argument('-j', "--jsonnet", action="store_true", default=False,
                            help="Experimental Jsonnet format")

    def _call(self):
        r = kpm.registry.Registry(self.registry_host)
        result = r.pull(self.package, version=self.version)
        p = kpm.packager.Package(result)
        if self.isjsonnet:
            manifestClass = kpm.manifest_jsonnet.ManifestJsonnet
        else:
            manifestClass = kpm.manifest.Manifest
        self.path = os.path.join(self.dest, manifestClass(p).package_name())
        p.extract(self.path)

    def _render_json(self):
        print json.dumps({"pull": self.package,
                          "extrated": self.path})

    def _render_console(self):
        print "Pull package: %s... \nExtract to %s" % (self.package, self.path)
