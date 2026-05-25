"""Integration tests: create, list, detail, groups, and vulnerabilities."""


def test_full_crud_flow_with_groups_and_vulns(client):
    """Create all entities, list them, get details, including groups and vulnerabilities."""

    # ── Create VmTemplate ──
    resp = client.post(
        "/vm-templates/",
        json={
            "name": "Windows Server 2022",
            "vm_id": 114,
            "description": "Base Windows template",
        },
    )
    assert resp.status_code == 200, resp.text
    vm_tpl = resp.json()
    assert vm_tpl["name"] == "Windows Server 2022"
    vm_template_id = vm_tpl["id"]

    # List vm-templates
    resp = client.get("/vm-templates/")
    assert resp.status_code == 200
    assert any(t["id"] == vm_template_id for t in resp.json())

    # ── Create Project ──
    resp = client.post("/projects/", json={"name": "GOT-Lab"})
    assert resp.status_code == 200, resp.text
    project_id = resp.json()["id"]

    # List projects
    resp = client.get("/projects/")
    assert resp.status_code == 200
    assert any(p["id"] == project_id for p in resp.json())

    # ── Create Forest ──
    resp = client.post(
        f"/projects/{project_id}/forests/",
        json={"fqdn": "GOT.LAN"},
    )
    assert resp.status_code == 200, resp.text
    forest_id = resp.json()["id"]

    # ── Create Domain ──
    resp = client.post(
        f"/forests/{forest_id}/domains/",
        json={"fqdn": "GOT.LAN"},
    )
    assert resp.status_code == 200, resp.text
    domain_id = resp.json()["id"]

    # ── Create Server (DC) ──
    resp = client.post(
        f"/domains/{domain_id}/servers/",
        json={
            "fqdn": "DC01.GOT.LAN",
            "is_dc": True,
            "ip": "192.168.30.10",
            "gtw": "192.168.30.254",
            "vm_template_id": vm_template_id,
        },
    )
    assert resp.status_code == 200, resp.text
    server = resp.json()
    assert server["is_dc"] is True
    assert server["vm_template_name"] == "Windows Server 2022"

    # ── Create Users ──
    users_payloads = [
        {"firstname": "Jon",      "lastname": "Snow",       "password": "Winter2026!",       "domain_id": domain_id},
        {"firstname": "Arya",     "lastname": "Stark",      "password": "Needle2026!",       "domain_id": domain_id},
        {"firstname": "Sansa",    "lastname": "Stark",      "password": "QueenInNorth2026!", "domain_id": domain_id},
        {"firstname": "Bran",     "lastname": "Stark",      "password": "ThreeEyed2026!",    "domain_id": domain_id},
        {"firstname": "Tyrion",   "lastname": "Lannister",  "password": "ImpsMind2026!",     "domain_id": domain_id},
        {"firstname": "Daenerys", "lastname": "Targaryen",  "password": "Dragons2026!",      "domain_id": domain_id},
        {"firstname": "Sandor",   "lastname": "Clegane",    "password": "Hound2026!",        "domain_id": domain_id},
    ]

    created_usernames = []
    created_users = []

    for payload in users_payloads:
        resp = client.post("/users/", json=payload)
        assert resp.status_code == 200, resp.text
        body = resp.json()
        created_usernames.append(body["username"])
        created_users.append(body)

    assert "j.snow" in created_usernames
    j_snow  = next(u for u in created_users if u["username"] == "j.snow")
    a_stark = next(u for u in created_users if u["username"] == "a.stark")
    s_stark = next(u for u in created_users if u["username"] == "s.stark")

    # ── GET project detail ──
    resp = client.get(f"/projects/{project_id}")
    assert resp.status_code == 200
    detail = resp.json()
    assert detail["project"]["name"] == "GOT-Lab"
    assert len(detail["forests"]) == 1
    assert detail["forests"][0]["fqdn"] == "GOT.LAN"
    assert len(detail["domains"]) == 1
    assert len(detail["servers"]) == 1
    assert detail["servers"][0]["fqdn"] == "DC01.GOT.LAN"
    assert len(detail["users"]) == 7
    assert "j.snow" in {u["username"] for u in detail["users"]}

    # ── Create Group "Starks" with Jon, Arya, Sansa ──
    user_ids = [u["id"] for u in created_users[:3]]
    resp = client.post(
        "/groups/",
        json={
            "name": "Starks",
            "description": "House Stark members",
            "user_ids": user_ids,
            "domain_id": domain_id,
        },
    )
    assert resp.status_code == 200, resp.text
    group_starks    = resp.json()
    group_starks_id = group_starks["id"]
    assert group_starks["name"] == "Starks"
    assert set(group_starks["user_ids"]) == set(user_ids)

    # ── Create Group "NorthLords" with Bran, Tyrion ──
    north_user_ids = [created_users[3]["id"], created_users[4]["id"]]
    resp = client.post(
        "/groups/",
        json={
            "name": "NorthLords",
            "description": "Northern lords group",
            "user_ids": north_user_ids,
            "domain_id": domain_id,
        },
    )
    assert resp.status_code == 200, resp.text
    group_northlords    = resp.json()
    group_northlords_id = group_northlords["id"]
    assert set(group_northlords["user_ids"]) == set(north_user_ids)

    # ── List & detail groups ──
    resp = client.get("/groups/")
    assert resp.status_code == 200
    groups_list = resp.json()
    assert any(g["id"] == group_starks_id     for g in groups_list)
    assert any(g["id"] == group_northlords_id  for g in groups_list)

    resp = client.get(f"/groups/{group_starks_id}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Starks"
    assert set(resp.json()["user_ids"]) == set(user_ids)

    resp = client.get(f"/groups/{group_northlords_id}")
    assert resp.status_code == 200
    assert set(resp.json()["user_ids"]) == set(north_user_ids)

    # ─────────────────────────────────────────────────────────────────
    # ── VULNERABILITIES ──────────────────────────────────────────────
    # ─────────────────────────────────────────────────────────────────

    # 1) Récupérer le catalogue  →  GET /vulnerabilities/
    resp = client.get("/vulnerabilities/")
    assert resp.status_code == 200
    vuln_catalog = resp.json()
    vuln_by_code = {v["code"]: v for v in vuln_catalog}

    for expected_code in ("asrep_roasting", "kerberoasting", "genericall_dacl",
                          "writedacl", "forcechangepassword", "dcsync"):
        assert expected_code in vuln_by_code, f"Missing vuln in catalogue: {expected_code}"

    # Helper pour créer une vuln appliquée  →  POST /vulnerabilities/projects/{project_id}
    def apply_vuln(code: str, params: dict) -> int:
        r = client.post(
            f"/vulnerabilities/projects/{project_id}",
            json={
                "vuln_id":   vuln_by_code[code]["id"],
                "domain_id": domain_id,
                "params":    params,
            },
        )
        assert r.status_code == 200, f"[{code}] {r.text}"
        return r.json()["id"]

    applied_ids = []

    # 2) AS-REP Roasting  →  user Jon Snow
    applied_ids.append(apply_vuln("asrep_roasting", {
        "username": j_snow["username"],
    }))

    # 3) Kerberoasting  →  user Arya Stark
    applied_ids.append(apply_vuln("kerberoasting", {
        "username": a_stark["username"],
        "spn_name": "HTTP/dc01.got.lan",
    }))

    # 4) GenericAll DACL  →  source = groupe "Starks", target = user Sansa
    applied_ids.append(apply_vuln("genericall_dacl", {
        "source_username": "Starks",
        "target_username": s_stark["username"],
    }))

    # 5) WriteDACL  →  source = user Jon, target = groupe "Starks"
    applied_ids.append(apply_vuln("writedacl", {
        "source_username": j_snow["username"],
        "target_username": "Starks",
    }))

    # 6) ForceChangePassword  →  source = groupe "NorthLords", target = user Arya
    applied_ids.append(apply_vuln("forcechangepassword", {
        "source_username": "NorthLords",
        "target_username": a_stark["username"],
    }))

    # 7) DCSync  →  source = groupe "NorthLords" sur le domaine
    applied_ids.append(apply_vuln("dcsync", {
        "username":  "NorthLords",
        "domain_dn": "DC=got,DC=lan",
    }))

    # ── Vérifier que toutes les vulns sont listées pour ce projet ──
    resp = client.get(f"/vulnerabilities/projects/{project_id}")
    assert resp.status_code == 200
    applied_list = resp.json()
    applied_ids_in_db = {v["id"] for v in applied_list}
    for vid in applied_ids:
        assert vid in applied_ids_in_db, f"Applied vuln {vid} not found in project list"

    # ── Vérifier qu'on ne peut pas créer deux fois la même vuln avec les mêmes params ──
    resp = client.post(
        f"/vulnerabilities/projects/{project_id}",
        json={
            "vuln_id":   vuln_by_code["asrep_roasting"]["id"],
            "domain_id": domain_id,
            "params":    {"username": j_snow["username"]},
        },
    )
    assert resp.status_code == 409, f"Expected 409 on duplicate vuln, got {resp.status_code}"

    # ── Delete une vuln appliquée et vérifier qu'elle disparaît ──
    vuln_to_delete = applied_ids[0]
    resp = client.delete(f"/vulnerabilities/{vuln_to_delete}")
    assert resp.status_code == 200
    assert resp.json()["message"] == "Vulnerability removed successfully"

    resp = client.get(f"/vulnerabilities/projects/{project_id}")
    assert resp.status_code == 200
    remaining_ids = {v["id"] for v in resp.json()}
    assert vuln_to_delete not in remaining_ids