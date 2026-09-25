import database


def test_policy_status_is_scoped_to_authenticated_user(monkeypatch):
    documents = [
        {"id": "policy_document:one", "user_id": "user:one", "status": "processed", "processing_status": "done"},
        {"id": "policy_document:two", "user_id": "user:two", "status": "processed", "processing_status": "done"},
    ]
    monkeypatch.setattr(database.db, "select", lambda table: documents if table == "policy_document" else [])

    status = database.get_policy_status_for_user("user:one")

    assert status["has_document"] is True
    assert status["document_count"] == 1
    assert status["document_id"] == "policy_document:one"


def test_processing_document_counts_without_triggering_upload_prompt(monkeypatch):
    documents = [{
        "id": "policy_document:processing",
        "user_id": "user:one",
        "status": "uploaded",
        "processing_status": "processing",
    }]
    monkeypatch.setattr(database.db, "select", lambda table: documents if table == "policy_document" else [])

    status = database.get_policy_status_for_user("user:one")

    assert status["has_document"] is True
    assert status["status"] == "processing"
