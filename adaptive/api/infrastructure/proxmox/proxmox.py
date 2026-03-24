import logging
import time
from typing import Any

from proxmoxer import ProxmoxAPI

from adaptive.api.environment.config import settings
from adaptive.api.exceptions import (
    ProxmoxConnectionError,
    ProxmoxTaskError,
    ProxmoxTimeoutError,
    ServerMissingTemplateError,
)
from adaptive.api.infrastructure.base import CloneResult, HypervisorProvider, ServerInfo

logger = logging.getLogger(__name__)

PREFIX = "[PROXMOX]"


class ProxmoxProvider(HypervisorProvider):
    def __init__(
        self,
        host: str | None = None,
        user: str | None = None,
        password: str | None = None,
        node: str | None = None,
        verify_ssl: bool = False,
    ):
        self._host = host or settings.proxmox_host
        self._user = user or settings.proxmox_user
        self._password = password or settings.proxmox_password
        self._node = node or settings.proxmox_node
        self._verify_ssl = verify_ssl
        self._api: Any = None
        logger.info("%s Provider initialized (host=%s, node=%s)", PREFIX, self._host, self._node)

    def check_connection(self) -> dict:
        version = self.api.version.get()
        return {
            "status": "connected",
            "host": self._host,
            "node": self._node,
            "version": version.get("version"),
        }

    @property
    def api(self) -> Any:
        if self._api is None:
            logger.info("%s Connecting to Proxmox at %s...", PREFIX, self._host)
            try:
                self._api = ProxmoxAPI(
                    self._host,
                    user=self._user,
                    password=self._password,
                    verify_ssl=self._verify_ssl,
                )
            except Exception as exc:
                raise ProxmoxConnectionError(self._host, str(exc)) from exc
            logger.info("%s Connected successfully", PREFIX)
        return self._api

    def deploy_lab(self, servers: list[ServerInfo]) -> list[CloneResult]:
        logger.info(
            "%s Starting lab deployment: %d servers",
            PREFIX,
            len(servers),
        )
        results: list[CloneResult] = []
        for server in servers:
            try:
                result = self.clone_vm(server)
                results.append(result)
            except Exception as e:
                logger.error("%s Failed to clone server %s: %s", PREFIX, server.fqdn, e)
                results.append(CloneResult(success=False, server_id=server.id, error=str(e)))

        succeeded = sum(1 for r in results if r.success)
        logger.info(
            "%s Lab deployment finished: %d/%d VMs cloned successfully",
            PREFIX,
            succeeded,
            len(servers),
        )
        return results

    def clone_vm(self, server: ServerInfo) -> CloneResult:
        if server.template_vm_id is None:
            raise ServerMissingTemplateError(server.id, server.fqdn)
        template_id = server.template_vm_id
        logger.info("%s Cloning template %d -> '%s'...", PREFIX, template_id, server.fqdn)

        new_vm_id = int(self.api.cluster.nextid.get())
        logger.debug("%s Next available VMID: %d", PREFIX, new_vm_id)

        task_upid = str(
            self.api.nodes(self._node)
            .qemu(template_id)
            .clone.post(newid=new_vm_id, name=server.fqdn, full=0)
        )
        logger.debug("%s Clone task started: %s", PREFIX, task_upid)

        self._wait_for_task(task_upid)
        logger.info("%s Clone completed for '%s' (vm_id=%d)", PREFIX, server.fqdn, new_vm_id)

        # self._configure_cloudinit(new_vm_id, server)
        self.start_vm(new_vm_id)

        return CloneResult(success=True, server_id=server.id, vm_id=new_vm_id)

    def _configure_cloudinit(self, vm_id: int, server: ServerInfo) -> None:
        if not server.ip:
            logger.warning("%s No IP for VM %d, skipping cloud-init config", PREFIX, vm_id)
            return

        ipconfig = f"ip={server.ip}"
        if server.gtw:
            ipconfig += f",gw={server.gtw}"
        config: dict[str, str] = {"ipconfig0": ipconfig}
        if server.dns:
            config["nameserver"] = server.dns

        logger.info("%s Configuring cloud-init for VM %d: %s", PREFIX, vm_id, config)
        self.api.nodes(self._node).qemu(vm_id).config.put(**config)

    def start_vm(self, vm_id: int) -> bool:
        logger.info("%s Starting VM %d...", PREFIX, vm_id)
        self.api.nodes(self._node).qemu(vm_id).status.start.post()
        ok = self._wait_for_status(vm_id, "running", timeout=120, initial_wait=5)
        if ok:
            logger.info("%s VM %d started successfully", PREFIX, vm_id)
        else:
            logger.warning("%s VM %d failed to start within timeout", PREFIX, vm_id)
        return ok

    def stop_vm(self, vm_id: int) -> bool:
        logger.info("%s Stopping VM %d...", PREFIX, vm_id)
        self.api.nodes(self._node).qemu(vm_id).status.stop.post()
        ok = self._wait_for_status(vm_id, "stopped", timeout=120, initial_wait=5)
        if ok:
            logger.info("%s VM %d stopped successfully", PREFIX, vm_id)
        else:
            logger.warning("%s VM %d failed to stop within timeout", PREFIX, vm_id)
        return ok

    def restart_vm(self, vm_id: int) -> bool:
        logger.info("%s Restarting VM %d (stop + start)...", PREFIX, vm_id)
        self.stop_vm(vm_id)
        return self.start_vm(vm_id)

    def _check_vm_status(self, vm_id: int, expected: str) -> bool:
        vm_info: dict[str, Any] = self.api.nodes(self._node).qemu(vm_id).status.current.get()
        status = vm_info.get("status")
        logger.debug("%s VM %d status: '%s' (expected: '%s')", PREFIX, vm_id, status, expected)
        return status == expected

    def _wait_for_status(
        self,
        vm_id: int,
        expected: str,
        timeout: int = 120,
        initial_wait: int = 0,
        poll_interval: int = 5,
    ) -> bool:
        if initial_wait:
            logger.debug("%s Waiting %ds before polling VM %d...", PREFIX, initial_wait, vm_id)
            time.sleep(initial_wait)

        elapsed = 0
        while elapsed < timeout:
            if self._check_vm_status(vm_id, expected):
                return True
            time.sleep(poll_interval)
            elapsed += poll_interval

        logger.error(
            "%s Timeout (%ds) waiting for VM %d to reach '%s'",
            PREFIX,
            timeout,
            vm_id,
            expected,
        )
        return False

    def _wait_for_task(self, task_upid: str, timeout: int = 300, poll_interval: int = 5) -> None:
        logger.debug("%s Waiting for task %s (timeout=%ds)...", PREFIX, task_upid, timeout)
        start_time = time.time()

        while True:
            elapsed = time.time() - start_time
            if elapsed > timeout:
                raise ProxmoxTimeoutError(task_upid, timeout)

            task_info: dict[str, Any] = self.api.nodes(self._node).tasks(task_upid).status.get()
            status = task_info.get("status")
            exitstatus = task_info.get("exitstatus")

            if status == "stopped" and exitstatus == "OK":
                logger.debug(
                    "%s Task %s completed successfully (%.1fs)",
                    PREFIX,
                    task_upid,
                    elapsed,
                )
                return
            if status == "stopped":
                raise ProxmoxTaskError(task_upid, exitstatus)

            logger.debug("%s Task %s in progress... (%.0fs elapsed)", PREFIX, task_upid, elapsed)
            time.sleep(poll_interval)
