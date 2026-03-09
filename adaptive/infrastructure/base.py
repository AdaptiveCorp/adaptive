from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ServerInfo:
    id: int
    fqdn: str
    ip: str | None
    vm_id: int | None


@dataclass
class CloneResult:
    success: bool
    server_id: int
    vm_id: int | None = None
    error: str | None = None


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
