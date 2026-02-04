# tests/test_transaction.py

def test_high_risk_transaction_denied(client, token):
    response = client.post(
        "/transaction",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "account": "account-12345",
            "amount": 1000,
            "action": "transfer_funds",
            "resource": "account-12345"
        }
    )

    assert response.status_code == 403


def test_low_risk_transaction_allowed(client, token):
    response = client.post(
        "/transaction",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "account": "account-12345",
            "amount": 50,
            "action": "view_balance",
            "resource": "account-12345"
        }
    )

    assert response.status_code == 200

def test_medium_risk_allowed(client, token):
    response = client.post(
        "/transaction",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "account": "account-12345",
            "amount": 100,
            "action": "view_balance",
            "resource": "account-12345"
        }
    )

    assert response.status_code == 200

def test_account_ownership_violation(client, token):
    response = client.post(
        "/transaction",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "account": "account-99999",
            "amount": 50,
            "action": "transfer_funds",
            "resource": "account-99999"
        }
    )

    assert response.status_code == 403
