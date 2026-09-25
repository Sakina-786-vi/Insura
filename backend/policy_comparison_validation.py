from collections.abc import Mapping
from typing import Any


class PolicyComparisonValidationError(ValueError):
    """Raised when n8n does not return a valid policy comparison object."""


COMPARISON_FIELDS = (
    "field",
    "old_value",
    "new_value",
    "change_type",
    "importance",
    "explanation",
)


def normalize_policy_comparison_response(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, Mapping):
        raise PolicyComparisonValidationError("n8n response must be a JSON object")

    if "output" not in payload:
        raise PolicyComparisonValidationError("n8n response is missing the output object")

    output = payload.get("output")
    if not isinstance(output, Mapping):
        raise PolicyComparisonValidationError("n8n response is missing the output object")

    summary = output.get("summary")
    changes = output.get("changes")
    if not isinstance(changes, list):
        raise PolicyComparisonValidationError("comparison response is missing a changes array")
    if summary is not None and not isinstance(summary, str):
        raise PolicyComparisonValidationError("comparison summary must be a string or null")

    normalized_changes = []
    for index, change in enumerate(changes):
        if not isinstance(change, Mapping):
            raise PolicyComparisonValidationError(f"comparison change {index} must be an object")

        normalized_change = dict(change)
        for field in COMPARISON_FIELDS:
            value = change.get(field)
            if value is not None and not isinstance(value, str):
                raise PolicyComparisonValidationError(
                    f"comparison change {index} field {field} must be a string or null"
                )
        normalized_changes.append(normalized_change)

    return {"summary": summary, "changes": normalized_changes}