import kpm.deploy
from kpm.commands.deploy import DeployCmd


class RemoveCmd(DeployCmd):
    name = 'remove'
    help_message = "remove a package from kubernetes"

    def _call(self):
        self.status = kpm.deploy.delete(self.package,
                                        version=self.version,
                                        dest=self.tmpdir,
                                        namespace=self.namespace,
                                        force=self.force,
                                        dry=self.dry_run,
                                        endpoint=self.registry_host,
                                        proxy=self.api_proxy,
                                        variables=self.variables,
                                        shards=self.shards,
                                        fmt=self.output)
