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


def test_create_user_reconnects_after_closed_surreal_socket(monkeypatch):
    from websockets.exceptions import ConnectionClosedError

    import database

    class StaleClient:
        def __init__(self):
            self.closed = False

        def create(self, table, user_data):
            raise ConnectionClosedError.__new__(ConnectionClosedError)

        def close(self):
            self.closed = True

    class FreshClient:
        def __init__(self):
            self.signed_in = False
            self.database = None

        def signin(self, credentials):
            self.signed_in = True

        def use(self, namespace, name):
            self.database = (namespace, name)

        def create(self, table, user_data):
            return {"id": "user:reconnected", **user_data}

    stale_client = StaleClient()
    fresh_client = FreshClient()
    monkeypatch.setattr(database, "db", stale_client)
    monkeypatch.setattr(database, "Surreal", lambda _url: fresh_client)

    user = database.create_user({"name": "Test User", "email": "test@example.invalid"})

    assert stale_client.closed
    assert fresh_client.signed_in
    assert fresh_client.database == (database.SURREALDB_NAMESPACE, database.SURREALDB_DATABASE)
    assert user["id"] == "user:reconnected"
