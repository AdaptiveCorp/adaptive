"""Integration tests: create, list, detail, and delete via API endpoints."""


def test_full_crud_flow(client):
    """Create all entities, list them, get details, then delete."""

    # ── Create VmTemplate ──
    resp = client.post(
        "/vm-templates/",
        json={
            "name": "Windows Server 2022",
            "vm_id": 107,
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
            "ip": "10.0.0.3",
            "gtw": "10.0.0.1",
            "vm_template_id": vm_template_id,
        },
    )
    assert resp.status_code == 200, resp.text
    server = resp.json()
    assert server["is_dc"] is True
    assert server["vm_template_name"] == "Windows Server 2022"

    # ── Create Users ──
    users_payloads = [
        {"firstname": "Jon", "lastname": "Snow", "password": "Winter2026!", "domain_id": domain_id},
        {"firstname": "Arya", "lastname": "Stark", "password": "Needle2026!", "domain_id": domain_id},
        {"firstname": "Sansa", "lastname": "Stark", "password": "QueenInNorth2026!", "domain_id": domain_id},
        {"firstname": "Bran", "lastname": "Stark", "password": "ThreeEyed2026!", "domain_id": domain_id},
        {"firstname": "Tyrion", "lastname": "Lannister", "password": "ImpsMind2026!", "domain_id": domain_id},
        {"firstname": "Daenerys", "lastname": "Targaryen", "password": "Dragons2026!", "domain_id": domain_id},
        {"firstname": "Sandor", "lastname": "Clegane", "password": "Hound2026!", "domain_id": domain_id},
    ]

    created_usernames = []

    for payload in users_payloads:
        resp = client.post("/users/", json=payload)
        assert resp.status_code == 200, resp.text
        created_usernames.append(resp.json()["username"])

    assert "j.snow" in created_usernames

    # ── GET project detail (lists everything) ──
    resp = client.get(f"/projects/{project_id}")
    assert resp.status_code == 200
    detail = resp.json()

    assert detail["project"]["name"] == "GOT-Lab"
    assert len(detail["forests"]) == 1
    assert detail["forests"][0]["fqdn"] == "GOT.LAN"
    assert len(detail["domains"]) == 1
    assert len(detail["servers"]) == 1
    assert detail["servers"][0]["fqdn"] == "DC01.GOT.LAN"

    # on s'attend maintenant à 7 users au total
    assert len(detail["users"]) == 7
    usernames_in_detail = {u["username"] for u in detail["users"]}
    assert "j.snow" in usernames_in_detail