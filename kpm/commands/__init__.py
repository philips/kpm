from kpm.commands.push import PushCmd
from kpm.commands.pull import PullCmd
from kpm.commands.version import VersionCmd
from kpm.commands.new import NewCmd
from kpm.commands.show import ShowCmd
from kpm.commands.login import LoginCmd


all_commands = {
    PushCmd.name: PushCmd,
    VersionCmd.name: VersionCmd,
    PullCmd.name: PullCmd,
    NewCmd.name: NewCmd,
    ShowCmd.name: ShowCmd,
    LoginCmd.name: LoginCmd,
}
