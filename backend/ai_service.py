import json
import logging
import os
import re
from collections.abc import Mapping
from typing import Any

import requests


logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are INSURA's insurance education assistant. For questions about the user's policy, use ONLY the supplied policy context. Never invent coverage, limits, deductibles, co-pay, waiting periods, exclusions, documents, claim eligibility, or reimbursement amounts. If a policy fact is unavailable, say exactly: This is not specified in your policy. For general insurance questions, give accurate general educational guidance and clearly say it is not a statement about the user's policy. Do not give definitive claim approval or rejection. Never use information from another user or policy."""


class AIServiceError(Exception):
    """Raised when the configured AI provider cannot produce a safe response."""


class AIService:
    def __init__(self, config: Mapping[str, Any] | None = None):
        settings = config or os.environ
        groq_key = str(settings.get("GROQ_API_KEY", "")).strip()
        self.api_key = str(settings.get("AI_API_KEY", "")).strip() or groq_key
        self.provider = str(settings.get("AI_PROVIDER", "groq" if groq_key else "openai-compatible")).strip().lower()
        self.task = str(settings.get("AI_TASK", "chat")).strip().lower()
        self.model = str(settings.get("AI_MODEL", "")).strip() or str(settings.get("GROQ_MODEL", "")).strip()
        self.base_url = str(settings.get("AI_BASE_URL", "")).strip().rstrip("/") or ("https://api.groq.com/openai/v1" if groq_key else "")
        self.timeout = float(settings.get("AI_TIMEOUT", 30) or 30)
        self.http = requests.Session()
        self.last_usage: dict[str, Any] = {}

    def analyze_simulation(self, question: str, policy_context: Mapping[str, Any]) -> dict[str, Any]:
        if not self.api_key or not self.model or not self.base_url:
            raise AIServiceError("AI service is not configured")

        schema = {
            "scenario_title": "string",
            "summary": "string",
            "coverage_status": "covered|not_specified|excluded|partially_applicable",
            "what_policy_says": "string",
            "relevant_coverage": ["string"],
            "limits": ["string"],
            "cost_considerations": ["string"],
            "waiting_period": "string",
            "exclusions": ["string"],
            "documents": ["string"],
            "claim_path": ["string"],
            "what_to_check": ["string"],
            "confidence": "high|medium|low",
            "policy_evidence": [{"field": "string", "value": "string"}],
        }
        user_prompt = json.dumps({"question": question, "policy_context": policy_context, "response_schema": schema}, ensure_ascii=False)
        messages = [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": user_prompt}]
        payload = {"model": self.model, "messages": messages, "temperature": 0.1, "response_format": {"type": "json_object"}}

        try:
            response = self._post(messages, payload)
            response.raise_for_status()
            body = response.json()
            self.last_usage = body.get("usage") if isinstance(body.get("usage"), dict) else {}
            content = self._content(body)
            parsed = self._parse_json(content)
            if parsed is not None:
                return parsed

            correction = messages + [
                {"role": "assistant", "content": str(content or "")},
                {"role": "user", "content": "Return the same answer as valid JSON only, matching the response schema. Do not add commentary."},
            ]
            payload["messages"] = correction
            retry = self._post(correction, payload)
            retry.raise_for_status()
            retry_body = retry.json()
            self.last_usage = retry_body.get("usage") if isinstance(retry_body.get("usage"), dict) else {}
            retry_content = self._content(retry_body)
            parsed = self._parse_json(retry_content)
            if parsed is None:
                raise AIServiceError("AI returned malformed JSON")
            return parsed
        except AIServiceError:
            raise
        except (requests.RequestException, ValueError, KeyError, IndexError, TypeError) as exc:
            logger.error("AI simulation request failed: %s", type(exc).__name__)
            raise AIServiceError("AI simulation request failed") from exc

    def answer_policy_chat(self, question: str, policy_context: Mapping[str, Any]) -> str:
        if not self.api_key or not self.model or not self.base_url:
            raise AIServiceError("AI service is not configured")
        try:
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT + " Answer the user's insurance question concisely. Return plain text, not JSON."},
                {"role": "user", "content": json.dumps({"question": question, "policy_context": policy_context}, ensure_ascii=False, default=str)},
            ]
            payload = {"model": self.model, "messages": messages, "temperature": 0.1}
            response = self._post(messages, payload)
            response.raise_for_status()
            body = response.json()
            self.last_usage = body.get("usage") if isinstance(body.get("usage"), dict) else {}
            content = self._content(body)
            if not isinstance(content, str) or not content.strip():
                raise AIServiceError("AI returned an empty chat response")
            return content.strip()
        except AIServiceError:
            raise
        except (requests.RequestException, ValueError, KeyError, IndexError, TypeError) as exc:
            logger.error("AI policy chat request failed: %s", type(exc).__name__)
            raise AIServiceError("AI policy chat request failed") from exc

    def _post(self, messages: list[dict[str, str]], payload: dict[str, Any]):
        if self.provider == "bytez":
            if self.task == "text-generation":
                prompt = "\n\n".join(f"{message['role'].upper()}: {message['content']}" for message in messages)
                return self.http.post(
                    f"{self.base_url}/{self.model}",
                    headers={"Authorization": self.api_key, "Content-Type": "application/json"},
                    json={"text": prompt, "params": {"temperature": 0.1}},
                    timeout=self.timeout,
                )
            return self.http.post(
                f"{self.base_url}/{self.model}",
                headers={"Authorization": self.api_key, "Content-Type": "application/json"},
                json={"messages": messages, "params": {"temperature": 0.1}},
                timeout=self.timeout,
            )
        return self.http.post(
            f"{self.base_url}/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            json=payload,
            timeout=self.timeout,
        )

    @staticmethod
    def _content(body: Any) -> Any:
        if isinstance(body, dict) and "output" in body:
            output = body["output"]
            if isinstance(output, dict):
                return output
            return output
        return body.get("choices", [{}])[0].get("message", {}).get("content") if isinstance(body, dict) else None

    @staticmethod
    def _parse_json(content: Any) -> dict[str, Any] | None:
        if isinstance(content, dict):
            return content
        if not isinstance(content, str):
            return None
        text = content.strip()
        text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.IGNORECASE)
        try:
            value = json.loads(text)
        except json.JSONDecodeError:
            return None
        return value if isinstance(value, dict) else None
