import logging
import os
from collections.abc import Mapping
from typing import Any

import requests


logger = logging.getLogger(__name__)


class N8NServiceError(Exception):
    """Raised when an n8n workflow cannot be called or returns invalid data."""


class N8NService:
    def __init__(self, config: Mapping[str, Any] | None = None):
        settings = config or os.environ
        self.policy_intelligence_url = settings.get("N8N_POLICY_INTELLIGENCE_URL", "")
        self.policy_comparison_url = settings.get("N8N_POLICY_COMPARISON_URL", "")
        self.learning_generation_url = settings.get("N8N_LEARNING_GENERATION_URL", "")
        self.timeout = self._parse_timeout(settings.get("N8N_TIMEOUT", ""))
        self.http = requests.Session()

    @staticmethod
    def _parse_timeout(value: Any) -> float:
        if value in (None, ""):
            return 20.0

        try:
            timeout = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError("N8N_TIMEOUT must be a positive number of seconds") from exc

        if timeout <= 0:
            raise ValueError("N8N_TIMEOUT must be a positive number of seconds")
        return timeout

    def run_policy_intelligence(
        self,
        *,
        filename: str,
        user_email: str,
        user_name: str,
        file_content: bytes | None = None,
        file_path: str | None = None,
    ) -> Any:
        if file_content is None and file_path is None:
            raise ValueError("Either file_content or file_path is required")

        if file_content is None:
            with open(file_path, "rb") as file_handle:
                file_content = file_handle.read()

        return self._post(
            workflow="policy intelligence",
            url=self.policy_intelligence_url,
            files={"policy": (filename, file_content, "application/pdf")},
            data={
                "user_email": user_email,
                "user_name": user_name,
                "source": "insura",
            },
        )

    def run_policy_comparison(
        self,
        *,
        old_filename: str,
        old_file_content: bytes,
        renewed_filename: str,
        renewed_file_content: bytes,
    ) -> Any:
        return self._post(
            workflow="policy comparison",
            url=self.policy_comparison_url,
            files={
                "old_policy": (old_filename, old_file_content, "application/pdf"),
                "renewed_policy": (renewed_filename, renewed_file_content, "application/pdf"),
            },
        )

    def run_learning_generation(self, payload: Mapping[str, Any]) -> Any:
        return self._post_json("learning generation", self.learning_generation_url, payload)

    def _post_json(self, workflow: str, url: str, payload: Mapping[str, Any]) -> Any:
        return self._post(workflow=workflow, url=url, json=dict(payload))

    def _post(self, workflow: str, url: str, **request_kwargs: Any) -> Any:
        if not url:
            logger.error("n8n %s workflow is not configured", workflow)
            raise N8NServiceError(f"n8n {workflow} workflow is not configured")

        try:
            response = self.http.post(url, timeout=self.timeout, **request_kwargs)
            response.raise_for_status()
        except requests.Timeout as exc:
            logger.error("n8n %s workflow timed out after %s seconds", workflow, self.timeout)
            raise N8NServiceError(f"n8n {workflow} workflow timed out") from exc
        except requests.ConnectionError as exc:
            logger.error("Could not connect to n8n %s workflow", workflow)
            raise N8NServiceError(f"Could not connect to n8n {workflow} workflow") from exc
        except requests.HTTPError as exc:
            status_code = exc.response.status_code if exc.response is not None else "unknown"
            logger.error("n8n %s workflow returned HTTP %s", workflow, status_code)
            raise N8NServiceError(f"n8n {workflow} workflow returned an HTTP error") from exc
        except requests.RequestException as exc:
            logger.error("n8n %s workflow request failed: %s", workflow, type(exc).__name__)
            raise N8NServiceError(f"n8n {workflow} workflow request failed") from exc

        try:
            return response.json()
        except ValueError as exc:
            logger.error("n8n %s workflow returned a non-JSON response", workflow)
            raise N8NServiceError(f"n8n {workflow} workflow returned invalid JSON") from exc