from app import (
    build_default_progression,
    calculate_progression_snapshot,
    compute_user_readiness,
    handle_progression_activity,
    resolve_deduplicated_policy_record,
)
from app import compute_user_streak
from app import PROGRESSION_XP_AWARDS


def test_learning_xp_awards_match_product_rules():
    assert PROGRESSION_XP_AWARDS["learning_question_correct"] == 10
    assert PROGRESSION_XP_AWARDS["learning_question_wrong"] == -5
    assert PROGRESSION_XP_AWARDS["learning_scenario"] == 10


def test_streak_accepts_surreal_datetime_values():
    assert compute_user_streak(["2026-09-24 07:57:39.453963+00:00"]) == 1


def test_user_progress_update_repairs_missing_created_at(monkeypatch):
    import database

    existing = {"id": "user_progress:one", "user_id": "user_1", "created_at": None}
    captured = {}

    monkeypatch.setattr(database, "get_user_progress", lambda user_id: existing)
    monkeypatch.setattr(database.db, "update", lambda record_id, payload: captured.update({"id": record_id, "payload": payload}) or payload)

    result = database.create_or_update_user_progress("user_1", {"xp": 10})

    assert result["created_at"] is not None
    assert result["updated_at"] is not None
    assert result["user_id"] == "user_1"


def test_resolve_deduplicated_policy_record_uses_stored_policy_data(monkeypatch):
    stored_policy = {
        "id": "policy_analysis:stored",
        "analysis_id": "analysis-123",
        "extracted_data": {"coverage": 82},
    }

    monkeypatch.setattr(
        "app.find_policy_document_by_hash",
        lambda user_id, document_hash: {"user_id": user_id, "document_hash": document_hash, "policy_id": "analysis-123"},
    )
    monkeypatch.setattr("app.get_policy_analysis_by_analysis_id", lambda policy_id: stored_policy if policy_id == "analysis-123" else None)
    monkeypatch.setattr("app.get_latest_user_policy", lambda user_id: {"id": "fallback", "analysis_id": "fallback-analysis", "extracted_data": {"coverage": 1}})

    resolved = resolve_deduplicated_policy_record("user_1", "hash-abc")

    assert resolved == stored_policy
    assert resolved["extracted_data"]["coverage"] == 82


def test_default_progression_starts_at_zero():
    state = build_default_progression()
    assert state["xp"] == 0
    assert state["streak"] == 0
    assert state["readiness"] == 0
    assert state["completed_levels"] == 0


def test_learning_level_completion_is_only_awarded_once():
    first = handle_progression_activity(
        user_id="user_1",
        activity_type="learning_level",
        activity_id="level_01",
        current_snapshot={"xp": 0, "streak": 0, "readiness": 0, "completed_levels": 0, "badges": [], "transactions": []},
    )
    second = handle_progression_activity(
        user_id="user_1",
        activity_type="learning_level",
        activity_id="level_01",
        current_snapshot={"xp": 0, "streak": 0, "readiness": 0, "completed_levels": 0, "badges": [], "transactions": first["transactions"]},
    )

    assert first["xp"] == 50
    assert second["xp"] == 0
    assert len(first["transactions"]) == 1
    assert len(second["transactions"]) == 1


def test_learning_progress_uses_xp_streak_and_badges():
    snapshot = calculate_progression_snapshot(
        xp=150,
        completed_levels=3,
        total_levels=5,
        readiness=55,
        streak=4,
    )
    assert snapshot["xp"] == 150
    assert snapshot["learning_percentage"] == 12
    assert snapshot["readiness"] == 55
    assert snapshot["streak"] == 4


def test_learning_progress_never_reaches_one_hundred_percent():
    snapshot = calculate_progression_snapshot(
        xp=5000,
        completed_levels=999,
        total_levels=1,
        streak=365,
        badges=["badge"] * 20,
    )

    assert snapshot["learning_percentage"] == 99


def test_policy_upload_sets_base_readiness_to_fifteen_percent():
    readiness = compute_user_readiness(
        has_policy=True,
        learning_completions=[],
        total_levels=5,
    )
    assert readiness == 15


def test_daily_learning_readiness_caps_at_two_percent():
    readiness = compute_user_readiness(
        has_policy=True,
        learning_completions=[
            {"completed_at": "2026-09-24T09:00:00Z"},
            {"completed_at": "2026-09-24T10:00:00Z"},
            {"completed_at": "2026-09-24T11:00:00Z"},
            {"completed_at": "2026-09-24T12:00:00Z"},
            {"completed_at": "2026-09-24T13:00:00Z"},
        ],
        total_levels=5,
    )
    assert readiness == 17
