import os
import json
import base64
import kpm.registry
from kpm.manifest_jsonnet import ManifestJsonnet
from kpm.packager import pack_kub
from kpm.commands.command_base import CommandBase


class PushCmd(CommandBase):
    name = 'push'
    help_message = "push a package to the registry"

    def __init__(self, options):
        self.output = options.output
        self.registry_host = options.registry_host
        self.force = options.force
        self.manifest = None

        super(PushCmd, self).__init__(options)

    @classmethod
    def _add_arguments(self, parser):
        parser.add_argument("-H", "--registry-host", nargs="?", default=kpm.registry.DEFAULT_REGISTRY,
                            help='registry API url')
        parser.add_argument("-o", "--organization", nargs="?", default=None,
                            help="push to another organization")
        parser.add_argument("-f", "--force", action='store_true', default=False,
                            help="force push")

    def _call(self):
        r = kpm.registry.Registry(self.registry_host)
        # @TODO: Override organization
        self.manifest = ManifestJsonnet()
        # @TODO: Pack in memory
        kubepath = os.path.join(".", self.manifest.package_name() + "kub.tar.gz")
        pack_kub(kubepath)
        f = open(kubepath, 'rb')
        r.push(self.manifest.package['name'], {"name": self.manifest.package['name'],
                                               "version": self.manifest.package['version'],
                                               "blob": base64.b64encode(f.read())}, self.force)
        f.close()
        os.remove(kubepath)

    def _render_json(self):
        print json.dumps({"package": self.manifest.package['name'],
                          "version": self.manifest.package['version']})

    def _render_console(self):
        print "package: %s (%s) pushed" % (self.manifest.package['name'],
                                           self.manifest.package['version'])
