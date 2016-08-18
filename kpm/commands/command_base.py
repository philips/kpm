class CommandBase(object):
    name = 'command-base'
    help_message = 'describe the command'

    def __init__(self, args_options):
        pass

    def render(self):
        if self.output == 'json':
            self._render_json()
        else:
            self._render_console()

    @classmethod
    def call(self, options):
        self(options)()

    def __call__(self):
        self._call()
        self.render()

    @classmethod
    def add_parser(self, subparsers):
        parser = subparsers.add_parser(self.name, help=self.help_message)
        parser.add_argument("--output", default="text",  choices=['text', 'json'],
                            help="output format")
        self._add_arguments(parser)
        parser.set_defaults(func=self.call)

    def _render_json(self):
        raise NotImplementedError

    def _render_console(self):
        raise NotImplementedError

    def _call(self):
        raise NotImplementedError

    @classmethod
    def _add_arguments(self, parser):
        raise NotImplementedError
