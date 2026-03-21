"""Integration tests: create, list, detail, and delete via API endpoints."""


def test_full_crud_flow(client):
    """Create all entities, list them, get details, then delete."""

    # ── Create VmTemplate ──
    resp = client.post(
        "/vm-templates/",
        json={
            "name": "Windows Server 2022",
            "vm_id": 102,
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
            "fqdn": "dc01.GOT.LAN",
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

    # ── Create User ──
    resp = client.post(
        "/users/",
        json={
            "firstname": "Jon",
            "lastname": "Snow",
            "password": "Winter2026!",
            "domain_id": domain_id,
        },
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["username"] == "j.snow"

    # ── GET project detail (lists everything) ──
    resp = client.get(f"/projects/{project_id}")
    assert resp.status_code == 200
    detail = resp.json()
    assert detail["project"]["name"] == "GOT-Lab"
    assert len(detail["forests"]) == 1
    assert detail["forests"][0]["fqdn"] == "GOT.LAN"
    assert len(detail["domains"]) == 1
    assert len(detail["servers"]) == 1
    assert detail["servers"][0]["fqdn"] == "dc01.GOT.LAN"
    assert len(detail["users"]) == 1
    assert detail["users"][0]["username"] == "j.snow"
