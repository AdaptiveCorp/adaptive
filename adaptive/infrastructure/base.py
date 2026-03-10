from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class ServerInfo:
    id: int
    fqdn: str
    ip: str | None = None


@dataclass
class CloneResult:
    success: bool
    server_id: int
    vm_id: int | None = None
    error: str | None = None


@dataclass
class DeploymentResult:
    project_name: str
    success: bool
    message: str | None = None
    error: str | None = None
    clone_results: list[CloneResult] = field(default_factory=list)


class HypervisorProvider(ABC):
    @abstractmethod
    def deploy_lab(
        self, servers: list[ServerInfo], template_id: int = 101
    ) -> list[CloneResult]:
        ...

    @abstractmethod
    def clone_vm(self, server: ServerInfo, template_id: int) -> CloneResult:
        ...

    @abstractmethod
    def start_vm(self, vm_id: int) -> bool:
        ...

    @abstractmethod
    def restart_vm(self, vm_id: int) -> bool:
        ...

    @abstractmethod
    def stop_vm(self, vm_id: int) -> bool:
        ...
