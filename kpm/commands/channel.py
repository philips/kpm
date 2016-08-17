import json
import argparse
import kpm.registry
from kpm.commands.command_base import CommandBase


class ChannelCmd(CommandBase):
    name = 'channel'
    help_message = "Manage package channels"

    def __init__(self, options):
        self.output = options.output
        self.package = options.package[0]
        self.registry_host = options.registry_host
        self.create = options.create
        self.remove = options.remove
        self.add = options.add
        self.status = None
        self.channels = {}
        super(ChannelCmd, self).__init__(options)

    @classmethod
    def _add_arguments(self, parser):
        parser.add_argument("-n", "--name", nargs="?", default=None,
                            help="channel name")
        parser.add_argument("--add", nargs="?", default=None,
                            help="Add a release to the channel")
        parser.add_argument("--create", default=False, action='store_true',
                            help="Create the channel")
        parser.add_argument("--remove", nargs="?", default=None,
                            help="Remove a release from the channel")
        parser.add_argument("-H", "--registry-host", nargs="?", default=kpm.registry.DEFAULT_REGISTRY,
                            help='registry API url')
        parser.add_argument('package', nargs=1, help="package-name")

    def _call(self):
        r = kpm.registry.Registry(self.registry_host)
        package = self.package[0]
        name = self.name
        is_show = self.add is None and self.remove is None
        if self.name is None and not is_show:
            raise argparse.ArgumentError("missing channel name")

        if self.create is True:
            self.channels = r.create_channel(package, name)
            self.status = "Channel '%s' on '%s' created" % (name, package)
        elif is_show:
            self.channels = r.show_channels(package, self.name)
            # @TODO
            self.status = self.channels
        else:
            if self.add is not None:
                self.channels = r.create_channel_release(package, name, self.add)
                self.status = ">>> Release '%s' added on '%s'" % (self.add, name)
            if self.remove is not None:
                self.channels = r.delete_channel_release(package, name, self.remove)
                self.status = ">>> Release '%s' removed from '%s'" % (self.remove, name)

    def _render_json(self):
        print json.dumps(self.channels)

    def _render_console(self):
        print " >>> " % self.status
