import json
import kpm.registry
from kpm.commands.command_base import CommandBase
from kpm.auth import KpmAuth


class LogoutCmd(CommandBase):
    name = 'logout'
    help_message = "logout"

    def __init__(self, options):
        self.output = options.output
        self.registry_host = options.registry_host
        self.status = None
        super(LogoutCmd, self).__init__(options)

    @classmethod
    def _add_arguments(self, parser):
        parser.add_argument("-H", "--registry-host", nargs="?", default=kpm.registry.DEFAULT_REGISTRY,
                            help='registry API url')

    def _call(self):
        KpmAuth().delete_token()
        self.status = "Logout complete"

    def _render_json(self):
        print json.dumps({"status": self.status})

    def _render_console(self):
        print " >>> %s" % self.status
