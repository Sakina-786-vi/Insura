import base64
import os
from collections.abc import Mapping
from typing import Any

import requests


class SarvamServiceError(Exception):
    """Raised when Sarvam cannot complete an optional language operation."""


class SarvamService:
    base_url = "https://api.sarvam.ai"

    def __init__(self, config: Mapping[str, Any] | None = None):
        settings = config or os.environ
        self.api_key = str(settings.get("SARVAM_API_KEY", "")).strip()
        self.stt_model = str(settings.get("SARVAM_STT_MODEL", "saaras:v3")).strip()
        self.tts_model = str(settings.get("SARVAM_TTS_MODEL", "bulbul:v3")).strip()
        self.translation_model = str(settings.get("SARVAM_TRANSLATION_MODEL", "mayura:v1")).strip()
        self.timeout = float(settings.get("SARVAM_TIMEOUT", 30) or 30)
        self.http = requests.Session()

    @property
    def configured(self):
        return bool(self.api_key)

    def transcribe(self, audio: bytes, filename: str, content_type: str, language_code: str = "unknown") -> dict[str, Any]:
        self._require_key()
        response = self.http.post(
            f"{self.base_url}/speech-to-text",
            headers=self._headers(),
            files={"file": (filename, audio, content_type or "application/octet-stream")},
            data={"model": self.stt_model, "language_code": language_code or "unknown", "mode": "transcribe"},
            timeout=self.timeout,
        )
        return self._json(response, "Speech transcription failed")

    def translate(self, text: str, source_language_code: str, target_language_code: str) -> dict[str, Any]:
        self._require_key()
        response = self.http.post(
            f"{self.base_url}/translate",
            headers={**self._headers(), "Content-Type": "application/json"},
            json={
                "input": text,
                "source_language_code": source_language_code,
                "target_language_code": target_language_code,
                "model": self.translation_model,
            },
            timeout=self.timeout,
        )
        return self._json(response, "Translation failed")

    def synthesize(self, text: str, target_language_code: str) -> bytes:
        self._require_key()
        response = self.http.post(
            f"{self.base_url}/text-to-speech",
            headers={**self._headers(), "Content-Type": "application/json"},
            json={
                "text": text,
                "language_code": target_language_code,
                "speaker": "shubh",
                "model": self.tts_model,
                "pace": 1.0,
            },
            timeout=self.timeout,
        )
        payload = self._json(response, "Speech synthesis failed")
        audios = payload.get("audios") if isinstance(payload, dict) else None
        if not isinstance(audios, list) or not audios or not isinstance(audios[0], str):
            raise SarvamServiceError("Speech synthesis returned no audio")
        try:
            return b"".join(base64.b64decode(audio, validate=True) for audio in audios)
        except (ValueError, TypeError, base64.binascii.Error) as exc:
            raise SarvamServiceError("Speech synthesis returned invalid audio") from exc

    def _require_key(self):
        if not self.configured:
            raise SarvamServiceError("Sarvam is not configured")

    def _headers(self):
        return {"api-subscription-key": self.api_key}

    @staticmethod
    def _json(response, message):
        try:
            response.raise_for_status()
            payload = response.json()
        except (requests.RequestException, ValueError) as exc:
            raise SarvamServiceError(message) from exc
        if not isinstance(payload, dict):
            raise SarvamServiceError(message)
        return payload


sarvam_service = SarvamService()
