import tempfile
from pathlib import Path

import ansible_runner  # type: ignore


def dc_promote(
    server_ip: str,
    dc_hostname: str,
    domain_fqdn: str,
    domain_netbios: str,
    dsrm_password: str,
    is_first_dc: bool = True,
    domain_admin: str = None,
    forest_mode: str = "WinThreshold",
    domain_mode: str = "WinThreshold",
    install_dns: bool = True,
    ansible_user: str = "Administrator",
    ansible_password: str = "Azerty1234@",
):
    print(f"[>] Promotion du DC {dc_hostname} ({server_ip})...")
    print(f"    Domaine: {domain_fqdn}")
    print(f"    Premier DC: {is_first_dc}")

    playbook_path = (
        Path(__file__).parent.parent
        / "ansible"
        / "inventory"
        / "playbooks"
        / "dc_promo.yaml"
    )
    print(playbook_path)
    if not playbook_path.exists():
        raise FileNotFoundError(f"Playbook not found: {playbook_path}")

    inventory = {
        "all": {
            "hosts": {
                server_ip: {
                    "ansible_user": ansible_user,
                    "ansible_password": ansible_password,
                }
            }
        }
    }

    extravars = {
        "target_host": server_ip,
        "dc_hostname": dc_hostname,
        "domain_fqdn": domain_fqdn,
        "domain_netbios": domain_netbios,
        "dsrm_password": dsrm_password,
        "is_first_dc": is_first_dc,
        "forest_mode": forest_mode,
        "domain_mode": domain_mode,
        "install_dns": install_dns,
        "domain_admin": domain_admin or f"Administrator@{domain_fqdn}",
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        result = ansible_runner.run(
            private_data_dir=tmpdir,
            playbook=str(playbook_path),
            inventory=inventory,
            extravars=extravars,
            verbosity=2,
        )

        if result.status == "successful":
            print(f"[+] DC {dc_hostname} promu avec succès")
            return {
                "success": True,
                "dc_hostname": dc_hostname,
                "domain_fqdn": domain_fqdn,
                "server_ip": server_ip,
                "output": result.stdout.read() if result.stdout else "",
            }
        else:
            error_msg = result.stdout.read() if result.stdout else "Unknown error"
            print(f"[!] Erreur lors de la promotion : {error_msg}")
            return {"success": False, "error": error_msg, "return_code": result.rc}


def add_users(
    host: int,
    userslist,
    ansible_user: str = "Administrator",
    ansible_password: str = "Azerty1234@",
):

    return None
