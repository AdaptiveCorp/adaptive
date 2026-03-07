import time
from dataclasses import dataclass

from proxmoxer import ProxmoxAPI  # type: ignore

# Configuration Proxmox (à mettre dans config.py)
PROXMOX_HOST = "10.0.0.10"
PROXMOX_USER = "root@pam"
PROXMOX_PASSWORD = "adaptive"
PROXMOX_NODE = "pve-01"


@dataclass
class ServerInfo:
    """Données nécessaires pour cloner/déployer un serveur, sans dépendance DB."""

    id: int
    fqdn: str
    ip: str | None
    vm_id: int | None


def deploy_lab(servers: list[ServerInfo], template_id: int = 101) -> list[dict]:
    """
    Clone des VMs pour une liste de serveurs.

    :param servers: Liste de ServerInfo à déployer
    :param template_id: ID du template Proxmox source
    :return: Liste de résultats avec vm_id attribués
    """
    proxmox = get_proxmox_connection()

    print(f"[++] Clonage de {len(servers)} serveurs")

    results = []
    for server in servers:
        try:
            result = clone_vm(proxmox, server, template_id)
            results.append(result)
        except Exception as e:
            results.append({"success": False, "server_id": server.id, "error": str(e)})

    print("[++] Clonage terminé")
    return results


def clone_vm(proxmox, server: ServerInfo, template_id: int) -> dict:
    """
    Clone une VM pour un serveur.

    :param server: ServerInfo avec les données du serveur
    :param template_id: ID du template Proxmox source
    :return: Dict avec les infos de clonage, incluant le vm_id attribué
    """
    new_vm_id = 1000 + server.id
    vm_name = server.fqdn.split(".")[0]

    try:
        print(f"[>] Clonage VM du serveur {server.fqdn}...")
        task = (
            proxmox.nodes(PROXMOX_NODE)
            .qemu(template_id)
            .clone.post(newid=new_vm_id, name=server.fqdn, full=0)
        )
        print(f"[>] Tâche de clonage lancée : {task}")

        print("[>] Attente de la fin du clonage...")
        wait_for_task_completion(proxmox, task)

        start_vm(proxmox, new_vm_id)
        print(f"[+] VM {server.fqdn} clonée, ID --> {new_vm_id}")

        return {
            "success": True,
            "vm_id": new_vm_id,
            "vm_name": vm_name,
            "server_id": server.id,
            "task": task,
        }

    except Exception as e:
        raise Exception(f"[!] Erreur clonage VM : {e}")


def start_vm(proxmox, vm_id: int):
    """
    Démarre une VM Proxmox.
    """
    try:
        print(f"[>] Démarrage de la VM {vm_id}...")
        proxmox.nodes(PROXMOX_NODE).qemu(vm_id).status.start.post()

        time.sleep(3)

        vm_status = proxmox.nodes(PROXMOX_NODE).qemu(vm_id).status.current.get()

        if vm_status.get("status") == "running":
            print(f"[+] VM {vm_id} démarrée")
            return True
        else:
            print(f"[!] VM {vm_id} status: {vm_status.get('status')}")
            return False

    except Exception as e:
        print(f"[!] Erreur démarrage VM : {e}")
        return False


def get_proxmox_connection():
    """
    Créer une connexion Proxmox
    """
    try:
        proxmox = ProxmoxAPI(
            PROXMOX_HOST, user=PROXMOX_USER, password=PROXMOX_PASSWORD, verify_ssl=False
        )
        return proxmox
    except Exception as e:
        raise ConnectionError(f"[!] Erreur connexion Proxmox : {e}")


def wait_for_task_completion(
    proxmox, task_upid: str, timeout: int = 300, check_interval: int = 5
):
    """
    Attend la fin d'une tâche Proxmox

    :param proxmox: Connexion Proxmox
    :param task_upid: UPID de la tâche
    :param timeout: Temps max d'attente en secondes (défaut 5 min)
    :param check_interval: Intervalle entre les vérifications en secondes
    """
    start_time = time.time()

    while True:
        elapsed = time.time() - start_time

        if elapsed > timeout:
            raise TimeoutError(
                f"[!] Timeout après {timeout}s en attendant la tâche {task_upid}"
            )

        try:
            task_status = proxmox.nodes(PROXMOX_NODE).tasks(task_upid).status.get()
            status = task_status.get("status")
            exitstatus = task_status.get("exitstatus")

            if status == "stopped" and exitstatus == "OK":
                print("[+] Tâche terminée avec succès")
                return True

            elif status == "stopped":
                raise Exception(f"[!] Tâche échouée : {exitstatus}")

            else:
                print(f"[>] Tâche en cours... ({int(elapsed)}s écoulées)")
                time.sleep(check_interval)

        except Exception:
            print(f"[>] Vérification du statut... ({int(elapsed)}s)")
            time.sleep(check_interval)


def restart_vm(vm_id: int):
    """
    Redémarre une VM Proxmox.
    """
    proxmox = get_proxmox_connection()
    try:
        print(f"[>] Redémarrage de la VM {vm_id}...")

        proxmox.nodes(PROXMOX_NODE).qemu(vm_id).status.reboot.post()

        print(f"[+] Commande de redémarrage envoyée à la VM {vm_id}")

        print("[>] Attente de l'arrêt...")
        time.sleep(20)

        print("[>] Attente du redémarrage...")
        max_wait = 120
        elapsed = 0

        while elapsed < max_wait:
            vm_status = proxmox.nodes(PROXMOX_NODE).qemu(vm_id).status.current.get()  # type: ignore[union-attr]

            if vm_status.get("status") == "running":  # type: ignore[union-attr]
                print(f"[+] VM {vm_id} redémarrée avec succès")
                return True

            time.sleep(5)
            elapsed += 5

            if elapsed % 20 == 0:
                print(f"[>] Attente... {elapsed}s/{max_wait}s")

        print(f"[!] Timeout : VM {vm_id} n'a pas redémarré dans les temps")
        return False

    except Exception as e:
        print(f"[!] Erreur redémarrage VM : {e}")
        return False
