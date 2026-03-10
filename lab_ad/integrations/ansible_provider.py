import ansible_runner # type: ignore
import tempfile
from pathlib import Path
from ..database import orm_models
from sqlalchemy.orm import Session

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
    
    
    playbook_path = Path(__file__).parent.parent / "ansible" / "inventory" / "playbooks" / "dc_promo.yaml"
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
        "domain_admin": domain_admin or f"Administrator@{domain_fqdn}"
    }
    
    with tempfile.TemporaryDirectory() as tmpdir:

        result = ansible_runner.run(
            private_data_dir=tmpdir,
            playbook=str(playbook_path),
            inventory=inventory,
            extravars=extravars,
            verbosity=2
        )
        
        if result.status == "successful":
            print(f"[+] DC {dc_hostname} promu avec succès")
            return {
                "success": True,
                "dc_hostname": dc_hostname,
                "domain_fqdn": domain_fqdn,
                "server_ip": server_ip,
                "output": result.stdout.read() if result.stdout else ""
            }
        else:
            error_msg = result.stdout.read() if result.stdout else "Unknown error"
            print(f"[!] Erreur lors de la promotion : {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "return_code": result.rc
            }


def deploy_user(server_ip : str, fqdn : str, userslist, db: Session, ansible_user: str = "Administrator", ansible_password: str = "Azerty1234@"):
    # Pour les test l'ip du server est fixé
    users_list = []
    for user in userslist :
        user_data = {}
        user_data["username"] = user.username
        user_data["firstname"] = user.firstname
        user_data["lastname"] = user.lastname
        user_data["password"] = user.password + "Aaa"
        users_list.append(user_data)
    base_dn = "DC="+fqdn.split('.')[-2].lower()+","+"DC="+fqdn.split('.')[-1].lower()
    extravars = {
        "target_host": server_ip,
        "users_list" : users_list,
        "domain_fqdn" : fqdn,
        "base_dn" : base_dn 
    }

    playbook_path = Path(__file__).parent.parent / "ansible" / "inventory" / "playbooks" / "add_users.yaml"
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
    with tempfile.TemporaryDirectory() as tmpdir:

        result = ansible_runner.run(
            private_data_dir=tmpdir,
            playbook=str(playbook_path),
            inventory=inventory,
            extravars=extravars,
            verbosity=6
        )
        
    return None

def execute_powershell_winrm(
    server_ip: str, 
    powershell_script: str,
    params: dict,
    ansible_user: str = "Administrator",
    ansible_password: str = "Azerty1234@",
):
    print(f"[>] Exécution PowerShell sur {server_ip}")

    vars_block = "\n    ".join([f'{k}: "{v}"' for k, v in params.items()])
    
    indented_script = "\n        ".join(
        line for line in powershell_script.strip().splitlines()
    )
    playbook_content = f"""---
- name: Exécuter PowerShell
  hosts: {server_ip}
  gather_facts: false
  vars:
    {vars_block}
  tasks:
    - name: Run PowerShell script
      win_shell: |
        {indented_script}
      register: result
      ignore_errors: true

    - name: Debug output
      debug:
        var: result
"""

    
    inventory = {
        "all": {
            "hosts": {
                server_ip: {
                    "ansible_user": ansible_user,
                    "ansible_password": ansible_password,
                    "ansible_connection": "winrm",
                    "ansible_winrm_transport": "ntlm",
                    "ansible_winrm_server_cert_validation": "ignore",
                    "ansible_winrm_scheme": "http",
                    "ansible_port": 5985,
                }
            }
        }
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        playbook_path = Path(tmpdir) / "powershell.yaml"
        playbook_path.write_text(playbook_content)

        r = ansible_runner.run(
            private_data_dir=tmpdir,
            playbook=str(playbook_path),
            inventory=inventory,
            verbosity=2
        )

        
        output = r.stdout.read() if r.stdout else ""
        stderr = r.stderr.read() if r.stderr else ""
        status = r.status
        rc = r.rc

    
    return {
        "success": status == "successful",
        "output": output,
        "stderr": stderr,
        "return_code": rc
    }

