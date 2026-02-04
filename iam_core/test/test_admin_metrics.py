def test_admin_metrics(client, admin_token):
    response = client.get(
        "/admin/metrics",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == 200
    assert "deny_rate" in response.json()


    data = response.json()

    # Core metrics must exist
    assert "transactions" in data
    assert "deny_rate" in data
    assert "average_trust" in data
    assert "high_risk_events" in data
    assert "policy_denials" in data
