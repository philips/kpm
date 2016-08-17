import json
import kpm.registry
from kpm.commands.command_base import CommandBase


class DeletePackageCmd(CommandBase):
    name = 'delete-package'
    help_message = 'delete package from the registry'

    def __init__(self, options):
        self.output = options.output
        self.package = options.package[0]
        self.registry_host = options.registry_host
        self.version = options.version
        self.result = None
        super(DeletePackageCmd, self).__init__(options)

    @classmethod
    def _add_arguments(self, parser):
        parser.add_argument('package', nargs=1, help="package-name")
        parser.add_argument("-v", "--version", nargs="?",
                            help="package VERSION", default=None)
        parser.add_argument("-H", "--registry-host", nargs="?", default=kpm.registry.DEFAULT_REGISTRY,
                            help='registry API url')

    def _call(self):
        r = kpm.registry.Registry(self.registry_host)
        self.result = r.delete_package(self.package, version=self.version)

    def _render_json(self):
        print json.dumps(self.result)

    def _render_console(self):
        print "Deleted package: %s - %s" % (self.result['package'], self.result['version'])
