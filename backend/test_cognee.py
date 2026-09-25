"""Real extracted-policy smoke test for the local Cognee/LanceDB setup."""

from pathlib import Path

from cognee_service import CogneePolicyService
from database import db


def main():
    records = [record for record in (db.select("policy_analysis") or []) if record.get("extracted_data")]
    record = next(
        (
            item
            for item in records
            if (item.get("extracted_data") or {}).get("financial", {}).get("deductible")
        ),
        None,
    )
    if not record:
        raise RuntimeError("No stored extracted policy with a deductible is available for this smoke test")

    user_id = str(record["user_id"])
    policy_id = str(record.get("id") or record.get("analysis_id"))
    policy_payload = record["extracted_data"]
    expected_deductible = str(policy_payload["financial"]["deductible"])

    service = CogneePolicyService()
    status = service.health_check()
    assert status["initialized"] is True, status
    assert Path(status["storage_root"]).resolve() == service.storage_root.resolve()
    assert "site-packages" not in status["storage_root"].lower()

    assert service.index_policy(user_id, policy_id, policy_payload) is True
    storage_files = [path for path in service.storage_root.rglob("*") if path.is_file()]
    assert storage_files, f"Cognee storage is empty: {service.storage_root}"

    results = service.retrieve_policy(user_id, policy_id, "What is my deductible?", policy_payload)
    retrieved_context = "\n".join(results)
    assert expected_deductible in retrieved_context, retrieved_context

    print(f"storage_root={service.storage_root.resolve()}")
    print(f"policy_id={policy_id}")
    print(f"deductible={expected_deductible}")
    print(f"retrieval_results={len(results)}")
    print("COGNEE REAL POLICY INDEXING AND RETRIEVAL PASSED")


if __name__ == "__main__":
    main()
