import json
import logging
import textwrap
import time

import winrm
from sqlalchemy.orm import Session

from adaptive.api.environment.config import settings
from adaptive.api.infrastructure import AnsibleService, PlaybookResult

logger: logging.Logger = logging.getLogger(__name__)


def _bare_ip(ip: str) -> str:
    return ip.split("/")[0]


def _wait_for_adws(
    server_ip: str,
    timeout: int = 45,
    poll_interval: int = 15,
    initial_wait: int = 30,
) -> bool:
    """Poll a DC via WinRM until connection is successful, then enable ADWS."""
    if initial_wait:
        logger.info("[WAIT] Waiting %ds before checking WinRM on %s...", initial_wait, server_ip)
        time.sleep(initial_wait)

    session = winrm.Session(
        f"http://{server_ip}:5985/wsman",
        auth=(settings.ansible_user, settings.ansible_password),
        transport="ntlm",
    )

    elapsed = 0

    while elapsed < timeout:
        try:
            result = session.run_ps("echo ok")
            if result.status_code == 0:
                logger.info(
                    "[WAIT] WinRM is reachable on %s (after %ds)", server_ip, elapsed + initial_wait
                )

                logger.info("[WAIT] Enabling and starting ADWS on %s...", server_ip)
                adws_result = session.run_ps(
                    "Set-Service ADWS -StartupType Automatic; Start-Service ADWS"
                )

                if adws_result.status_code == 0:
                    logger.info("[WAIT] ADWS successfully started on %s", server_ip)
                else:
                    error_msg = adws_result.std_out.decode(errors="replace").strip()
                    logger.error("[WAIT] Failed to start ADWS on %s: %s", server_ip, error_msg)
                    return False

                return True

        except Exception as exc:
            logger.info(
                "[WAIT] Cannot reach %s yet (%s), retrying in %ds...",
                server_ip,
                type(exc).__name__,
                poll_interval,
            )

        time.sleep(poll_interval)
        elapsed += poll_interval

    logger.error("[WAIT] Timeout (%ds) waiting for WinRM on %s", timeout + initial_wait, server_ip)
    return False


def _wait_for_ad_ready(
    server_ip: str,
    timeout: int = 600,
    poll_interval: int = 30,
    initial_wait: int = 60,
) -> bool:
    """Attendre que le DC soit réellement fonctionnel (AD DS + ADWS)."""

    if initial_wait:
        logger.info("[WAIT] Waiting %ds before checking AD on %s...", initial_wait, server_ip)
        time.sleep(initial_wait)

    session = winrm.Session(
        f"http://{server_ip}:5985/wsman",
        auth=(settings.ansible_user, settings.ansible_password),
        transport="ntlm",
    )

    elapsed = 0

    while elapsed < timeout:
        try:
            ping = session.run_ps("echo ok")
            if ping.status_code != 0:
                raise RuntimeError("WinRM not ready yet")

            ps_script = r"""
            try {
                Import-Module ActiveDirectory -ErrorAction Stop
                $d = Get-ADDomain -ErrorAction Stop
                Write-Output "AD_READY"
                exit 0
            } catch {
                Write-Output "AD_NOT_READY: $($_.Exception.Message)"
                exit 1
            }
            """

            result = session.run_ps(ps_script)
            output = result.std_out.decode(errors="replace").strip()

            if result.status_code == 0 and "AD_READY" in output:
                logger.info(
                    "[WAIT] AD domain is ready on %s (after %ds)", server_ip, elapsed + initial_wait
                )
                return True

            logger.info(
                "[WAIT] AD not ready yet on %s (%s), retrying in %ds...",
                server_ip,
                output,
                poll_interval,
            )

        except Exception as exc:
            logger.info(
                "[WAIT] Cannot reach %s or AD not ready yet (%s), retrying in %ds...",
                server_ip,
                type(exc).__name__,
                poll_interval,
            )

        time.sleep(poll_interval)
        elapsed += poll_interval

    logger.error(
        "[WAIT] Timeout (%ds) waiting for AD readiness on %s", timeout + initial_wait, server_ip
    )
    return False


def execute_powershell_winrm(
    server_ip: str,
    powershell_script: str,
    params: dict,
    db: Session,
) -> PlaybookResult:
    ansible = AnsibleService(db=db)

    vars_lines = []
    for k, v in params.items():
        if isinstance(v, (list, dict)):
            vars_lines.append(f"    {k}: {json.dumps(v)}")
        else:
            vars_lines.append(f'    {k}: "{v}"')

    indented_script = textwrap.indent(powershell_script.strip(), "        ")
    playbook_content = "\n".join(
        [
            "- name: Exécuter PowerShell",
            f"  hosts: {server_ip}",
            "  gather_facts: false",
            "  vars:",
            "\n".join(vars_lines),
            "    ansible_connection: winrm",
            "    ansible_winrm_transport: ntlm",
            "    ansible_winrm_server_cert_validation: ignore",
            "    ansible_port: 5985",
            "    ansible_winrm_read_timeout_sec: 120",
            "",
            "  tasks:",
            "    - name: Run PowerShell script",
            "      win_shell: |",
            indented_script,
            "      register: result",
            "",
            "    - name: Debug output",
            "      debug:",
            "        var: result",
        ]
    )

    return ansible._run_playbook(playbook_content, server_ip, params)
