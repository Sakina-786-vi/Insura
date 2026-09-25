from app import app


def test_cors_allows_dynamic_frontend_origin():
    client = app.test_client()

    response = client.get(
        "/api/session",
        headers={"Origin": "http://127.0.0.1:5174"},
    )

    assert response.status_code == 200
    assert response.headers["Access-Control-Allow-Origin"] == "http://127.0.0.1:5174"


def test_google_auth_redirect_uses_runtime_backend_host():
    client = app.test_client()

    response = client.get(
        "/auth/google",
        headers={"Host": "localhost:5001"},
    )

    assert response.status_code == 302
    assert "localhost%3A5001%2Fauth%2Fgoogle%2Fcallback" in response.location
