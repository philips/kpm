import json
import kpm.registry
import kpm.packager
import kpm.manifest
import kpm.manifest_jsonnet
from kpm.commands.command_base import CommandBase


class ShowCmd(CommandBase):
    name = 'show'
    help_message = "print the package manifest"

    def __init__(self, options):
        self.output = options.output
        self.package = options.package[0]
        self.registry_host = options.registry_host
        self.version = options.version
        self.file = options.file
        self.tree = options.tree
        self.result = None
        super(ShowCmd, self).__init__(options)

    @classmethod
    def _add_arguments(self, parser):
        parser.add_argument('package', nargs=1, help="package-name")
        parser.add_argument('--tree', help="List files inside the package", action='store_true', default=False)
        parser.add_argument('-f', '--file', nargs="?", help="Display a file", default=None)
        parser.add_argument("-v", "--version", nargs="?", default=None,
                            help="package version")
        parser.add_argument("-H", "--registry-host", nargs="?", default=kpm.registry.DEFAULT_REGISTRY,
                            help='registry API url')

    def _call(self):
        r = kpm.registry.Registry(self.registry_host)
        result = r.pull(self.package, version=self.version)
        p = kpm.packager.Package(result)
        if self.tree:
            self.result = "\n".join(p.tree())
        elif self.file:
            self.result = p.file(self.file)
        else:
            self.result = p.manifest

    def _render_json(self):
        print json.dumps({"show": self.package,
                          "output": self.result})

    def _render_console(self):
        print self.result
