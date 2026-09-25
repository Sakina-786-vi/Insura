from collections.abc import Mapping
from typing import Any


class SimulationValidationError(ValueError):
    """Raised when a simulation response is missing its public contract."""


STATUSES = {"covered", "not_specified", "excluded", "partially_applicable", "likely_covered", "potentially_covered", "not_found", "likely_excluded"}
CONFIDENCES = {"high", "medium", "low"}


def _string(value: Any, fallback: str = "") -> str:
    return value if isinstance(value, str) else fallback


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]


def normalize_simulation_response(payload: Any, scenario: str) -> dict[str, Any]:
    if not isinstance(payload, Mapping):
        raise SimulationValidationError("Simulation response must be an object")
    output = payload.get("output", payload)
    if not isinstance(output, Mapping):
        raise SimulationValidationError("Simulation response is missing output")

    if not isinstance(output.get("coverage_status"), str):
        raise SimulationValidationError("Simulation response is missing coverage_status")
    if not isinstance(output.get("confidence"), str):
        raise SimulationValidationError("Simulation response is missing confidence")

    status = output["coverage_status"]
    confidence = output["confidence"]
    if status not in STATUSES:
        raise SimulationValidationError("Simulation response contains an invalid coverage_status")
    if confidence not in CONFIDENCES:
        raise SimulationValidationError("Simulation response contains an invalid confidence")

    financial = output.get("financial_considerations")
    if not isinstance(financial, Mapping):
        financial = {}

    relevant_coverage = _string_list(output.get("relevant_coverage"))
    cost_considerations = _string_list(output.get("cost_considerations"))
    what_to_check = _string_list(output.get("what_to_check"))
    exclusions = _string_list(output.get("exclusions"))
    evidence = output.get("policy_evidence")
    policy_evidence = [
        {"field": item.get("field"), "value": item.get("value")}
        for item in evidence or []
        if isinstance(item, Mapping) and isinstance(item.get("field"), str) and isinstance(item.get("value"), str)
    ] if isinstance(evidence, list) else []

    return {
        "scenario": _string(output.get("scenario"), scenario),
        "scenario_title": _string(output.get("scenario_title"), scenario),
        "summary": _string(output.get("summary"), _string(output.get("explanation"), "INSURA couldn't determine this from the available policy information.")),
        "coverage_status": status,
        "confidence": confidence,
        "what_policy_says": _string(output.get("what_policy_says"), _string(output.get("explanation"), "INSURA couldn't determine this from the available policy information.")),
        "explanation": _string(output.get("explanation"), _string(output.get("what_policy_says"), "INSURA couldn't determine this from the available policy information.")),
        "relevant_coverage": relevant_coverage,
        "policy_basis": _string_list(output.get("policy_basis")) or relevant_coverage,
        "cost_considerations": cost_considerations,
        "financial_considerations": {
            "deductible": _string(financial.get("deductible"), "Not specified in your uploaded policy."),
            "copay": _string(financial.get("copay"), "Not specified in your uploaded policy."),
            "limit": _string(financial.get("limit"), "Not specified in your uploaded policy."),
            "other_possible_cost": _string(financial.get("other_possible_cost"), "Not specified in your uploaded policy."),
        },
        "waiting_period": _string(output.get("waiting_period"), "Not specified in your uploaded policy."),
        "documents": _string_list(output.get("documents")),
        "next_steps": _string_list(output.get("next_steps")) or what_to_check,
        "what_to_check": what_to_check,
        "exclusions": exclusions,
        "missing_information": _string_list(output.get("missing_information")) or (["Not specified in the available policy information."] if status == "not_specified" else []),
        "limits": _string_list(output.get("limits")),
        "claim_path": _string_list(output.get("claim_path")),
        "policy_evidence": policy_evidence,
    }
