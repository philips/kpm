import json
from kpm.render_jsonnet import RenderJsonnet
from kpm.utils import parse_cmdline_variables
from kpm.commands.command_base import CommandBase


class JsonnetCmd(CommandBase):
    name = 'jsonnet'
    help_message = "Resolve a jsonnet file with the kpmstd available"

    def __init__(self, options):
        self.output = options.output
        self.shards = options.shards
        self.namespace = options.namespace
        self.variables = options.variables
        self.filepath = options.filepath[0]
        self.result = None

        super(JsonnetCmd, self).__init__(options)

    @classmethod
    def _add_arguments(self, parser):
        parser.add_argument("--namespace", nargs="?",
                            help="kubernetes namespace", default='default')
        parser.add_argument("-x", "--variables",
                            help="variables", default=None, action="append")
        # @TODO shards
        parser.add_argument("--shards",
                            help="Shards list/dict/count: eg. --shards=5 ; --shards='[{\"name\": 1, \"name\": 2}]'",
                            default=None)
        parser.add_argument('filepath', nargs=1, help="Fetch package from the registry")

    def _call(self):

        r = RenderJsonnet()
        namespace = self.namespace
        variables = {}
        if self.variables is not None:
            variables = parse_cmdline_variables(self.variables)
        variables['namespace'] = namespace
        tla_codes = {"variables": variables}
        p = open(self.filepath).read()
        self.result = r.render_jsonnet(p, tla_codes={"params": json.dumps(tla_codes)})

    def _render_json(self):
        print json.dumps(self.result, indent=2, separators=(',', ': '))

    def _render_console(self):
        self._render_json()
