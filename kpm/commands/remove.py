from kpm.utils import parse_cmdline_variables
import kpm.deploy
from kpm.commands.deploy import DeployCmd


class RemoveCmd(DeployCmd):
    name = 'remove'
    help_message = "remove a package from kubernetes"

    def _call(self):
        variables = None
        if self.variables is not None:
            variables = parse_cmdline_variables(self.variables)

        self.status = kpm.deploy.delete(self.package,
                                        version=self.version,
                                        dest=self.tmpdir,
                                        namespace=self.namespace,
                                        force=self.force,
                                        dry=self.dry_run,
                                        endpoint=self.registry_host,
                                        proxy=self.api_proxy,
                                        variables=variables,
                                        shards=self.shards,
                                        fmt=self.output)
