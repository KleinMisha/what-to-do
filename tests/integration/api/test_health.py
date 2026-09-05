from fastapi.testclient import TestClient


def test_health(client: TestClient) -> None:
    """Return a successful response from the health endpoint."""
    response = client.get("/health")

    assert response.status_code == 200
