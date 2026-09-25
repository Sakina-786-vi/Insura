import json

import pytest

from ai_service import AIService, AIServiceError


class FakeResponse:
    def __init__(self, body):
        self.body = body

    def raise_for_status(self):
        return None

    def json(self):
        return self.body


class FakeHTTP:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.payloads = []

    def post(self, url, **kwargs):
        self.payloads.append(kwargs["json"])
        return FakeResponse(next(self.responses))


def valid_output():
    return {
        "choices": [{"message": {"content": json.dumps({
            "scenario_title": "Hospitalization",
            "summary": "Policy-grounded answer",
            "coverage_status": "covered",
            "what_policy_says": "Hospitalization is listed as covered.",
            "relevant_coverage": ["Hospitalization"],
            "limits": [],
            "cost_considerations": [],
            "waiting_period": "Not specified in the available policy information.",
            "exclusions": [],
            "documents": [],
            "claim_path": [],
            "what_to_check": [],
            "confidence": "medium",
            "policy_evidence": [{"field": "hospitalization", "value": "true"}],
        })}}]
    }


def test_ai_service_sends_only_minimal_policy_context():
    service = AIService({"AI_API_KEY": "secret", "AI_MODEL": "model", "AI_BASE_URL": "https://ai.example"})
    http = FakeHTTP([valid_output()])
    service.http = http

    service.analyze_simulation("What if I am hospitalized?", {"coverage": {"hospitalization": True}})

    sent = json.dumps(http.payloads[0])
    assert "hospitalization" in sent
    assert "password" not in sent
    assert "user_id" not in sent
    assert "secret" not in sent


def test_ai_service_retries_malformed_json_once():
    service = AIService({"AI_API_KEY": "secret", "AI_MODEL": "model", "AI_BASE_URL": "https://ai.example"})
    http = FakeHTTP([
        {"choices": [{"message": {"content": "not json"}}]},
        valid_output(),
    ])
    service.http = http

    result = service.analyze_simulation("What if I need surgery?", {})

    assert result["coverage_status"] == "covered"
    assert len(http.payloads) == 2


def test_ai_service_rejects_malformed_json_after_retry():
    service = AIService({"AI_API_KEY": "secret", "AI_MODEL": "model", "AI_BASE_URL": "https://ai.example"})
    service.http = FakeHTTP([
        {"choices": [{"message": {"content": "bad"}}]},
        {"choices": [{"message": {"content": "still bad"}}]},
    ])

    with pytest.raises(AIServiceError):
        service.analyze_simulation("What if I need surgery?", {})


def test_ai_service_supports_bytez_rest_shape():
    service = AIService({
        "AI_PROVIDER": "bytez",
        "AI_API_KEY": "bytez-secret",
        "AI_MODEL": "Qwen/Qwen3-4B",
        "AI_BASE_URL": "https://api.bytez.com/models/v2",
    })
    http = FakeHTTP([{"output": json.loads(valid_output()["choices"][0]["message"]["content"])}])
    service.http = http

    result = service.analyze_simulation("What if I am hospitalized?", {"coverage": {"hospitalization": True}})

    assert result["coverage_status"] == "covered"


def test_ai_service_supports_bytez_text_generation_shape():
    service = AIService({
        "AI_PROVIDER": "bytez",
        "AI_TASK": "text-generation",
        "AI_API_KEY": "bytez-secret",
        "AI_MODEL": "enowx_temp",
        "AI_BASE_URL": "https://api.bytez.com/models/v2",
    })
    http = FakeHTTP([{"output": json.dumps(json.loads(valid_output()["choices"][0]["message"]["content"]))}])
    service.http = http

    result = service.analyze_simulation("What if I am hospitalized?", {"coverage": {"hospitalization": True}})

    assert result["coverage_status"] == "covered"
    assert "text" in http.payloads[0]
    assert "messages" not in http.payloads[0]
