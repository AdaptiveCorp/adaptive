import logging
import time

from proxmoxer import ProxmoxAPI  # type: ignore

from adaptive.environment.config import settings
from adaptive.infrastructure.base import CloneResult, HypervisorProvider, ServerInfo

logger = logging.getLogger(__name__)


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
        self._api: ProxmoxAPI | None = None

    @property
    def api(self) -> ProxmoxAPI:
        if self._api is None:
            self._api = ProxmoxAPI(
                self._host,
                user=self._user,
                password=self._password,
                verify_ssl=self._verify_ssl,
            )
            logger.info("Connected to Proxmox at %s", self._host)
        return self._api

    def deploy_lab(
        self, servers: list[ServerInfo], template_id: int = 101
    ) -> list[CloneResult]:
        logger.info("Cloning %d servers from template %d", len(servers), template_id)
        results = []
        for server in servers:
            try:
                result = self.clone_vm(server, template_id)
                results.append(result)
            except Exception as e:
                logger.error("Failed to clone server %s: %s", server.fqdn, e)
                results.append(
                    CloneResult(success=False, server_id=server.id, error=str(e))
                )
        return results

    def clone_vm(self, server: ServerInfo, template_id: int) -> CloneResult:
        new_vm_id = 1000 + server.id
        logger.info("Cloning VM for %s (vm_id=%d)...", server.fqdn, new_vm_id)

        task_upid = (
            self.api.nodes(self._node)
            .qemu(template_id)
            .clone.post(newid=new_vm_id, name=server.fqdn, full=0)
        )

        self._wait_for_task(task_upid)
        self.start_vm(new_vm_id)

        logger.info("VM %s cloned successfully (vm_id=%d)", server.fqdn, new_vm_id)
        return CloneResult(success=True, server_id=server.id, vm_id=new_vm_id)

    def start_vm(self, vm_id: int) -> bool:
        logger.info("Starting VM %d...", vm_id)
        self.api.nodes(self._node).qemu(vm_id).status.start.post()
        time.sleep(3)
        return self._check_vm_status(vm_id, "running")

    def stop_vm(self, vm_id: int) -> bool:
        logger.info("Stopping VM %d...", vm_id)
        self.api.nodes(self._node).qemu(vm_id).status.stop.post()
        time.sleep(3)
        return self._check_vm_status(vm_id, "stopped")

    def restart_vm(self, vm_id: int) -> bool:
        logger.info("Restarting VM %d...", vm_id)
        self.api.nodes(self._node).qemu(vm_id).status.reboot.post()
        return self._wait_for_status(vm_id, "running", timeout=120, initial_wait=20)

    def _check_vm_status(self, vm_id: int, expected: str) -> bool:
        status = (
            self.api.nodes(self._node).qemu(vm_id).status.current.get().get("status")
        )
        if status == expected:
            logger.info("VM %d is %s", vm_id, expected)
            return True
        logger.warning("VM %d status is '%s', expected '%s'", vm_id, status, expected)
        return False

    def _wait_for_status(
        self,
        vm_id: int,
        expected: str,
        timeout: int = 120,
        initial_wait: int = 0,
        poll_interval: int = 5,
    ) -> bool:
        if initial_wait:
            time.sleep(initial_wait)

        elapsed = 0
        while elapsed < timeout:
            if self._check_vm_status(vm_id, expected):
                return True
            time.sleep(poll_interval)
            elapsed += poll_interval

        logger.error(
            "Timeout waiting for VM %d to reach status '%s'", vm_id, expected
        )
        return False

    def _wait_for_task(
        self, task_upid: str, timeout: int = 300, poll_interval: int = 5
    ) -> None:
        start_time = time.time()

        while True:
            elapsed = time.time() - start_time
            if elapsed > timeout:
                raise TimeoutError(
                    f"Task {task_upid} timed out after {timeout}s"
                )

            task_status = (
                self.api.nodes(self._node).tasks(task_upid).status.get()
            )
            status = task_status.get("status")
            exitstatus = task_status.get("exitstatus")

            if status == "stopped" and exitstatus == "OK":
                logger.info("Task %s completed successfully", task_upid)
                return
            if status == "stopped":
                raise RuntimeError(f"Task {task_upid} failed: {exitstatus}")

            logger.debug("Task in progress... (%ds elapsed)", int(elapsed))
            time.sleep(poll_interval)
