from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from adaptive.api.models.vm_template import VmTemplateStatus


@dataclass
class ServerInfo:
    id: int
    fqdn: str
    ip: str | None = None
    gtw: str | None = None
    dns: str | None = None
    template_vm_id: int | None = None


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
    def check_connection(self) -> dict: ...

    @abstractmethod
    def deploy_lab(self, servers: list[ServerInfo]) -> list[CloneResult]: ...

    @abstractmethod
    def clone_vm(self, server: ServerInfo) -> CloneResult: ...

    @abstractmethod
    def start_vm(self, vm_id: int) -> bool: ...

    @abstractmethod
    def restart_vm(self, vm_id: int) -> bool: ...

    @abstractmethod
    def stop_vm(self, vm_id: int) -> bool: ...

    @abstractmethod
    def check_template_status(self, vm_id: int) -> VmTemplateStatus: ...

    @abstractmethod
    def delete_vm(self, vm_id: int) -> bool: ...
