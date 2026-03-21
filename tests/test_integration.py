"""Integration test: full entity creation flow."""


def test_full_entity_creation_flow(client):
    """VmTemplate -> Project -> Forest -> Domain -> Server -> User."""

    # 1. Create VmTemplate
    resp = client.post(
        "/vm-templates/",
        json={"name": "Windows Server 2022", "vm_id": 9000, "description": "Base Windows template"},
    )
    assert resp.status_code == 200, resp.text
    vm_tpl = resp.json()
    assert vm_tpl["name"] == "Windows Server 2022"
    assert vm_tpl["vm_id"] == 9000
    assert vm_tpl["description"] == "Base Windows template"
    vm_template_id = vm_tpl["id"]

    # 2. Create Project
    resp = client.post("/projects/", json={"name": "GOT-Lab"})
    assert resp.status_code == 200, resp.text
    project = resp.json()
    assert project["name"] == "GOT-Lab"
    assert "created_at" in project
    project_id = project["id"]

    # 3. Create Forest
    resp = client.post(f"/projects/{project_id}/forests/", json={"fqdn": "GOT.LAN"})
    assert resp.status_code == 200, resp.text
    forest = resp.json()
    assert forest["fqdn"] == "GOT.LAN"
    assert forest["project_id"] == project_id
    forest_id = forest["id"]

    # 4. Create Domain (root domain, same FQDN as forest)
    resp = client.post(f"/forests/{forest_id}/domains/", json={"fqdn": "GOT.LAN"})
    assert resp.status_code == 200, resp.text
    domain = resp.json()
    assert domain["fqdn"] == "GOT.LAN"
    assert domain["forest_id"] == forest_id
    domain_id = domain["id"]

    # 5. Create Server (DC)
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
    assert server["fqdn"] == "dc01.GOT.LAN"
    assert server["is_dc"] is True
    assert server["ip"] == "10.0.0.3"
    assert server["domain_id"] == domain_id
    assert server["vm_template_id"] == vm_template_id
    assert server["vm_template_name"] == "Windows Server 2022"

    # 6. Create User (linked to domain)
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
    user = resp.json()
    assert user["username"] == "j.snow"
    assert user["domain_id"] == domain_id
    assert user["server_id"] is None
