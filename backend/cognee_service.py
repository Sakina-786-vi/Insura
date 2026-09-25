"""Optional Cognee policy memory integration.

SurrealDB remains the source of truth. Cognee only receives the normalized
policy extraction and is never required for an API request to succeed.
"""

import asyncio
import hashlib
import json
import logging
import os
import threading
from collections.abc import Mapping
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class CogneePolicyService:
    def __init__(self, config: Mapping[str, Any] | None = None):
        settings = config or os.environ
        self.enabled = str(settings.get("COGNEE_ENABLED", "true")).strip().lower() in {"1", "true", "yes"}
        self.dataset_prefix = str(settings.get("COGNEE_DATASET_PREFIX", "insura_policy")).strip() or "insura_policy"
        self._indexed_content: dict[str, str] = {}
        self._initialization_lock = threading.Lock()
        self._index_lock = threading.Lock()
        self._cognee = None
        self._initialized = False
        self.storage_root = Path(__file__).resolve().parent / ".cognee_data"

    def initialize_cognee(self):
        if not self.enabled:
            return None
        if self._initialized:
            return self._cognee

        with self._initialization_lock:
            if self._initialized:
                return self._cognee

            storage_root = self.storage_root.resolve()
            for directory in (storage_root, storage_root / "system", storage_root / "data", storage_root / "cache", storage_root / "logs"):
                directory.mkdir(parents=True, exist_ok=True)
            os.environ.setdefault("SYSTEM_ROOT_DIRECTORY", str(storage_root / "system"))
            os.environ.setdefault("DATA_ROOT_DIRECTORY", str(storage_root / "data"))
            os.environ.setdefault("CACHE_ROOT_DIRECTORY", str(storage_root / "cache"))
            os.environ.setdefault("COGNEE_LOGS_DIR", str(storage_root / "logs"))

            import cognee

            cognee.config.system_root_directory(str(storage_root / "system"))
            cognee.config.data_root_directory(str(storage_root / "data"))
            cognee.config.set_vector_db_provider("lancedb")
            cognee.config.set_vector_db_url(str(storage_root / "system" / "databases" / "cognee.lancedb"))
            cognee.config.set_llm_provider("openai")
            cognee.config.set_llm_model(os.getenv("COGNEE_LLM_MODEL") or os.getenv("GROQ_MODEL") or "groq/qwen/qwen3.8-27b")
            cognee.config.set_llm_api_key(os.getenv("GROQ_API_KEY", "").strip())
            cognee.config.set_llm_endpoint(os.getenv("COGNEE_LLM_ENDPOINT") or "https://api.groq.com/openai/v1")
            cognee.config.set_llm_config({"llm_max_completion_tokens": 500})
            cognee.config.set_embedding_provider("fastembed")
            cognee.config.set_embedding_model("BAAI/bge-small-en-v1.5")
            cognee.config.set_embedding_dimensions(384)
            self._cognee = cognee
            self._initialized = True
            logger.info("Cognee initialized with project-local storage at %s", storage_root)
            return cognee

    def health_check(self) -> dict[str, Any]:
        try:
            cognee = self.initialize_cognee()
            return {"enabled": self.enabled, "initialized": cognee is not None, "storage_root": str(self.storage_root.resolve())}
        except Exception as exc:
            logger.exception("Cognee initialization failed")
            return {"enabled": self.enabled, "initialized": False, "storage_root": str(self.storage_root.resolve()), "error": type(exc).__name__}

    def index_policy(self, user_id: str, policy_id: str, policy_payload: Mapping[str, Any]) -> bool:
        if not self.enabled:
            return False

        try:
            cognee = self.initialize_cognee()
        except Exception:
            logger.exception("Cognee initialization failed; policy indexing skipped")
            return False
        if cognee is None:
            return False

        content = self._policy_text(user_id, policy_id, policy_payload)
        dataset_name = self._dataset_name(user_id, policy_id, content)
        content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
        if self._indexed_content.get(dataset_name) == content_hash:
            return True

        with self._index_lock:
            try:
                self._run(self._index(cognee, dataset_name, content))
                self._indexed_content[dataset_name] = content_hash
                logger.info("Cognee policy indexed successfully: dataset=%s", dataset_name)
                return True
            except Exception:
                logger.exception("Cognee policy indexing failed: dataset=%s", dataset_name)
                return False

    def retrieve_policy(self, user_id: str, policy_id: str, question: str, policy_payload: Mapping[str, Any]) -> list[str]:
        if not self.enabled:
            return []

        try:
            cognee = self.initialize_cognee()
        except Exception:
            logger.exception("Cognee initialization failed; policy retrieval skipped")
            return []
        if cognee is None:
            return []

        content = self._policy_text(user_id, policy_id, policy_payload)
        dataset_name = self._dataset_name(user_id, policy_id, content)
        try:
            results = self._run(cognee.search(
                query_text=question,
                datasets=[dataset_name],
                query_type=cognee.SearchType.CHUNKS,
                top_k=8,
            ))
        except Exception as exc:
            logger.warning("Cognee policy retrieval failed: %s", type(exc).__name__)
            return []

        return self._result_texts(results)

    async def _index(self, cognee: Any, dataset_name: str, content: str):
        await cognee.add(content, dataset_name=dataset_name, incremental_loading=True)
        await cognee.cognify(datasets=[dataset_name], incremental_loading=True)

    @staticmethod
    def _run(awaitable):
        return asyncio.run(awaitable)

    def _dataset_name(self, user_id: str, policy_id: str, content: str) -> str:
        scope = hashlib.sha256(f"{user_id}:{policy_id}:{content}".encode("utf-8")).hexdigest()[:40]
        return f"{self.dataset_prefix}_{scope}"

    @staticmethod
    def _policy_text(user_id: str, policy_id: str, policy_payload: Mapping[str, Any]) -> str:
        return "\n".join([
            "INSURA policy facts",
            f"Policy scope: {hashlib.sha256(f'{user_id}:{policy_id}'.encode('utf-8')).hexdigest()}",
            json.dumps(policy_payload, ensure_ascii=False, sort_keys=True, default=str),
        ])

    @staticmethod
    def _result_texts(results: Any) -> list[str]:
        if not isinstance(results, (list, tuple)):
            results = [results]
        texts = []
        for result in results:
            if isinstance(result, Mapping) and isinstance(result.get("search_result"), (list, tuple)):
                texts.extend(CogneePolicyService._result_texts(result["search_result"]))
                continue
            value = getattr(result, "text", None)
            if value is None and isinstance(result, Mapping):
                value = result.get("text") or result.get("content") or result.get("chunk")
            if value is None:
                value = str(result) if isinstance(result, str) else None
            if value and str(value).strip():
                texts.append(str(value).strip())
        return texts


cognee_policy_service = CogneePolicyService()
