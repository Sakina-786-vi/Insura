from collections.abc import Mapping
from typing import Any


class PolicyIntelligenceValidationError(ValueError):
    """Raised when n8n does not return a policy intelligence object."""


def _value(source: Mapping[str, Any], key: str) -> Any:
    return source.get(key)


def _object(source: Any, fields: tuple[str, ...]) -> dict[str, Any] | None:
    if not isinstance(source, Mapping):
        return None
    return {field: source.get(field) for field in fields}


def _string_list(source: Any) -> list[str]:
    if not isinstance(source, list):
        return []
    return [item for item in source if isinstance(item, str)]


def _waiting_periods(source: Any) -> list[dict[str, Any]]:
    if not isinstance(source, list):
        return []
    return [
        {"condition": item.get("condition"), "period": item.get("period")}
        for item in source
        if isinstance(item, Mapping)
    ]


def _premium_tables(source: Any) -> list[dict[str, Any]]:
    if not isinstance(source, list):
        return []
    fields = ("plan", "zone", "age_range", "sum_insured", "individual_premium", "family_premium")
    return [{field: item.get(field) for field in fields} for item in source if isinstance(item, Mapping)]


def _source_evidence(source: Any) -> list[dict[str, Any]]:
    if not isinstance(source, list):
        return []
    fields = ("field", "value", "evidence", "page")
    return [{field: item.get(field) for field in fields} for item in source if isinstance(item, Mapping)]


def normalize_policy_intelligence_response(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, Mapping):
        raise PolicyIntelligenceValidationError("n8n response must be a JSON object")

    output = payload.get("output")
    if not isinstance(output, Mapping):
        raise PolicyIntelligenceValidationError("n8n response is missing the output object")

    document = _object(output.get("document"), ("insurer", "product_name", "uin", "document_type"))
    coverage = _object(
        output.get("coverage"),
        ("sum_insured_options", "hospitalization", "day_care", "domiciliary", "ambulance", "health_checkup"),
    )
    if coverage is not None:
        coverage["sum_insured_options"] = _string_list(coverage["sum_insured_options"])

    financial = _object(output.get("financial"), ("premium_tables", "deductible", "copayment"))
    if financial is not None:
        financial["premium_tables"] = _premium_tables(financial["premium_tables"])

    limits = _object(output.get("limits"), ("room_rent", "icu", "cataract", "major_surgeries"))
    claim_process = _object(output.get("claim_process"), ("cashless", "reimbursement", "documents", "deadlines"))
    if claim_process is not None:
        for field in ("cashless", "reimbursement", "documents", "deadlines"):
            claim_process[field] = _string_list(claim_process[field])

    renewal = _object(output.get("renewal"), ("renewable", "conditions"))
    if renewal is not None:
        renewal["conditions"] = _string_list(renewal["conditions"])

    return {
        "document": document,
        "coverage": coverage,
        "financial": financial,
        "limits": limits,
        "waiting_periods": _waiting_periods(output.get("waiting_periods")),
        "exclusions": _string_list(output.get("exclusions")),
        "claim_process": claim_process,
        "renewal": renewal,
        "important_conditions": _string_list(output.get("important_conditions")),
        "source_evidence": _source_evidence(output.get("source_evidence")),
    }