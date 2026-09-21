from fastapi.testclient import TestClient


def test_health(api_client: TestClient) -> None:
    """Return a successful response from the health endpoint."""
    response = api_client.get("/health")

    assert response.status_code == 200
