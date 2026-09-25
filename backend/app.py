import hashlib
import ast
import base64
import html
import io
import json
import os
import re
import secrets
import uuid
from datetime import date, datetime, timedelta, timezone
from urllib.parse import unquote, urlparse

import qrcode

from flask import Flask, jsonify, redirect, request, send_file, session
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from auth import get_current_user, login_required, login_user, logout_user, register_oauth
from ai_service import AIService, AIServiceError
from config import Config
from cognee_service import cognee_policy_service
from database import (
    create_badge,
    create_chat,
    create_chat_message,
    create_learning_completion,
    create_learning_generation,
    create_or_update_user_progress,
    create_policy_analysis,
    create_policy_comparison,
    create_policy_document,
    create_policy_share,
    create_simulation_completion,
    create_user,
    create_xp_transaction,
    find_learning_completion,
    find_policy_document_by_hash,
    get_policy_share_by_token,
    get_policy_share_for_user,
    find_simulation_completion,
    find_user_by_email,
    find_user_by_google_id,
    find_xp_transaction,
    get_policy_analysis_by_analysis_id,
    get_policy_analysis_by_record_id,
    get_policy_documents_for_user,
    read_policy_document_bytes,
    get_badges_for_user,
    get_chat_for_user,
    get_chat_messages,
    get_chats_for_user,
    get_learning_generation,
    get_policy_analysis,
    get_user_progress,
    get_simulation_completions_for_user,
    get_policy_status_for_user,
    has_user_policy,
    update_chat,
    to_surreal_datetime,
)
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from learning_generation_validation import LearningGenerationValidationError, normalize_learning_generation_response
from n8n_service import N8NService, N8NServiceError
from policy_comparison_validation import PolicyComparisonValidationError, normalize_policy_comparison_response
from policy_validation import PolicyIntelligenceValidationError, normalize_policy_intelligence_response
from simulation_validation import SimulationValidationError, normalize_simulation_response
from sarvam_service import SarvamServiceError, sarvam_service

FRONTEND_URL = Config.FRONTEND_URL
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
MAX_POLICY_FILE_SIZE = 20 * 1024 * 1024
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def resolve_frontend_url(request_obj=None):
    configured_url = os.getenv("FRONTEND_URL")
    if configured_url:
        return configured_url.rstrip("/")

    if request_obj is None:
        return FRONTEND_URL.rstrip("/")

    for header_name in ("Origin", "Referer"):
        value = request_obj.headers.get(header_name)
        if not value:
            continue

        parsed = urlparse(value)
        if parsed.scheme and parsed.netloc:
            return f"{parsed.scheme}://{parsed.netloc}"

    return FRONTEND_URL.rstrip("/")


def resolve_backend_url(request_obj=None):
    configured_url = os.getenv("BACKEND_BASE_URL")
    if configured_url:
        return configured_url.rstrip("/")

    if request_obj is None:
        return "http://127.0.0.1:5000"

    return request_obj.url_root.rstrip("/")


def compute_document_hash(file_bytes: bytes) -> str:
    return hashlib.sha256(file_bytes).hexdigest()


def get_user_policy_records(user_id):
    try:
        records = []
        for record in __import__("database").db.select("policy_analysis") or []:
            if str(record.get("user_id", "")) == str(user_id):
                records.append(record)
        return sorted(records, key=lambda item: str(item.get("created_at") or ""), reverse=True)
    except Exception:
        return []


def get_user_learning_records(user_id):
    try:
        records = []
        for record in __import__("database").db.select("learning_generation") or []:
            if str(record.get("user_id", "")) == str(user_id):
                records.append(record)
        return sorted(records, key=lambda item: str(item.get("created_at") or ""), reverse=True)
    except Exception:
        return []


def get_latest_user_policy(user_id):
    records = get_user_policy_records(user_id)
    return records[0] if records else None


def resolve_deduplicated_policy_record(user_id, document_hash):
    existing_document = find_policy_document_by_hash(user_id, document_hash)
    if not existing_document:
        return None

    stored_policy_id = str(existing_document.get("policy_id") or "").strip()
    if stored_policy_id:
        policy_record = get_policy_analysis_by_analysis_id(stored_policy_id)
        if policy_record:
            return policy_record

        policy_record = get_policy_analysis_by_record_id(stored_policy_id)
        if policy_record:
            return policy_record

    return get_latest_user_policy(user_id)


def get_latest_user_learning(user_id):
    records = get_user_learning_records(user_id)
    return records[0] if records else None


def count_learning_items(learning_payload):
    if not isinstance(learning_payload, dict):
        return 0
    package = learning_payload.get("learning_package") or {}
    concepts = package.get("concepts") or []
    scenarios = package.get("scenarios") or []
    mcqs = package.get("mcqs") or []
    return max(len(concepts) + len(scenarios) + len(mcqs), 1)


XP_LEVEL_THRESHOLDS = [0, 100, 250, 500, 850, 1300, 1850, 2500]
PROGRESSION_XP_AWARDS = {
    "learning_question_correct": 10,
    "learning_question_wrong": -5,
    "learning_scenario": 10,
    "simulation_completion": 20,
    "simulation_steps_bonus": 10,
    "learning_level": 50,
    "lesson": 25,
    "simulation": 30,
    "quiz": 15,
    "daily_story": 10,
    "daily_bonus": 20,
}
READINESS_BASE_POLICY = 15
READINESS_PER_LEARNING_UNIT = 0.5
DAILY_LEARNING_READINESS_CAP = 2.0


def clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))


def compute_xp_level(total_xp):
    xp_total = int(total_xp or 0)
    level = 1
    next_level_xp = XP_LEVEL_THRESHOLDS[1]
    current_level_xp = 0

    for index, threshold in enumerate(XP_LEVEL_THRESHOLDS):
        if xp_total >= threshold:
            level = index + 1
            current_level_xp = threshold
            next_level_xp = XP_LEVEL_THRESHOLDS[min(index + 1, len(XP_LEVEL_THRESHOLDS) - 1)]

    if xp_total < 100:
        next_level_xp = 100
        current_level_xp = 0

    remaining = max(0, next_level_xp - xp_total)
    return {
        "level": level,
        "current_level_xp": current_level_xp,
        "next_level_xp": next_level_xp,
        "remaining": remaining,
    }


def compute_user_streak(activity_dates):
    normalized_dates = set()
    for activity_date in activity_dates:
        if not activity_date:
            continue
        if isinstance(activity_date, datetime):
            normalized_dates.add(activity_date.date().isoformat())
            continue
        if isinstance(activity_date, date):
            normalized_dates.add(activity_date.isoformat())
            continue

        text = str(activity_date).strip()
        if not text:
            continue
        try:
            parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
            normalized_dates.add(parsed.date().isoformat())
        except ValueError:
            normalized_dates.add(text.split("T", 1)[0].split(" ", 1)[0])

    normalized_dates = sorted(normalized_dates, reverse=True)
    if not normalized_dates:
        return 0

    today = datetime.now(timezone.utc).date().isoformat()
    if normalized_dates[0] == today:
        streak = 1
    else:
        streak = 0

    cursor = normalized_dates[0] if normalized_dates[0] != today else normalized_dates[1] if len(normalized_dates) > 1 else None
    if cursor is None:
        return streak

    current_date = datetime.strptime(cursor, "%Y-%m-%d").date()
    while cursor in normalized_dates:
        streak += 1
        previous_day = current_date - timedelta(days=1)
        next_cursor = previous_day.isoformat()
        if next_cursor not in normalized_dates:
            break
        cursor = next_cursor
        current_date = previous_day
    return streak


def calculate_readiness(policy_payload, learning_payload, progress_payload=None):
    has_policy = bool(policy_payload)
    total_completed = int((progress_payload or {}).get("completed_levels", 0) or 0)
    learning_completions = []
    if isinstance(progress_payload, dict):
        learning_completions = list(progress_payload.get("learning_completions") or [])
    readiness = compute_user_readiness(has_policy=has_policy, learning_completions=learning_completions, total_levels=max(1, int((progress_payload or {}).get("total_levels", 5) or 5)))
    return int(readiness)


def compute_user_readiness(has_policy=False, learning_completions=None, total_levels=5):
    daily_totals = {}
    for completion in learning_completions or []:
        completed_at = completion.get("completed_at") if isinstance(completion, dict) else completion
        if not completed_at:
            continue
        try:
            parsed = __import__("datetime").datetime.fromisoformat(str(completed_at).replace("Z", "+00:00"))
            day_key = parsed.date().isoformat()
        except ValueError:
            day_key = str(completed_at).split("T")[0]
        gain = float(completion.get("readiness_gain", READINESS_PER_LEARNING_UNIT)) if isinstance(completion, dict) else READINESS_PER_LEARNING_UNIT
        daily_totals[day_key] = daily_totals.get(day_key, 0.0) + gain

    learning_gain = sum(min(total, DAILY_LEARNING_READINESS_CAP) for total in daily_totals.values())
    readiness = READINESS_BASE_POLICY if has_policy else 0
    readiness += learning_gain
    return int(round(clamp(readiness, 0, 100)))


def build_default_progression():
    return {
        "xp": 0,
        "streak": 0,
        "readiness": 0,
        "completed_levels": 0,
        "total_levels": 5,
        "learning_percentage": 0,
        "level": 1,
        "next_milestone_xp": 100,
        "badges": [],
        "transactions": [],
        "milestone": {"name": "First Steps", "remaining_xp": 100},
    }


def calculate_learning_percentage(xp=0, streak=0, badges=None):
    xp_score = min(100, max(0, float(xp or 0) / 10))
    streak_score = min(100, max(0, float(streak or 0) / 30 * 100))
    badge_score = min(100, max(0, len(badges or []) / 8 * 100))
    return min(99, max(0, int(round(xp_score * 0.6 + streak_score * 0.25 + badge_score * 0.15))))


def calculate_progression_snapshot(xp=0, completed_levels=0, total_levels=5, readiness=0, streak=0, badges=None, transactions=None):
    total_levels = max(int(total_levels or 5), 1)
    learning_percentage = calculate_learning_percentage(xp=xp, streak=streak, badges=badges)
    xp_level = compute_xp_level(int(xp or 0))
    level = xp_level["level"]
    next_milestone_xp = xp_level["remaining"]
    milestone_name = "First Steps"
    if xp_level["level"] >= 2:
        milestone_name = "Policy Explorer"
    if xp_level["level"] >= 3:
        milestone_name = "Knowledge Builder"
    if xp_level["level"] >= 5:
        milestone_name = "Insurance Ready"

    snapshot = {
        "xp": int(xp or 0),
        "streak": int(streak or 0),
        "readiness": max(0, min(100, int(readiness or 0))),
        "completed_levels": int(completed_levels or 0),
        "total_levels": total_levels,
        "learning_percentage": learning_percentage,
        "level": level,
        "next_milestone_xp": next_milestone_xp,
        "badges": badges or [],
        "transactions": transactions or [],
        "milestone": {"name": milestone_name, "remaining_xp": next_milestone_xp},
    }
    return snapshot


def handle_progression_activity(user_id, activity_type, activity_id, current_snapshot=None):
    base_snapshot = build_default_progression()
    current = dict(base_snapshot)
    if isinstance(current_snapshot, dict):
        current.update(current_snapshot)

    existing = [
        item for item in current.get("transactions", []) or []
        if str(item.get("activity_type", "")) == str(activity_type) and str(item.get("activity_id", "")) == str(activity_id)
    ]
    if existing:
        return calculate_progression_snapshot(
            xp=current.get("xp", 0),
            completed_levels=current.get("completed_levels", 0),
            total_levels=current.get("total_levels", 5),
            readiness=current.get("readiness", 0),
            streak=current.get("streak", 0),
            badges=current.get("badges", []),
            transactions=current.get("transactions", []),
        )

    xp_award = {
        "learning_level": 50,
        "lesson": 25,
        "simulation": 30,
        "quiz": 15,
        "daily_story": 10,
        "daily_bonus": 20,
    }.get(str(activity_type), 0)

    transactions = list(current.get("transactions", []) or [])
    if xp_award:
        transactions.append({"activity_type": activity_type, "activity_id": activity_id, "xp": xp_award})

    updated_xp = int(current.get("xp", 0) or 0) + xp_award
    completed_levels = int(current.get("completed_levels", 0) or 0)
    if str(activity_type) == "learning_level":
        completed_levels += 1

    readiness = int(current.get("readiness", 0) or 0)
    if str(activity_type) == "learning_level":
        readiness = min(100, readiness + 0)

    return calculate_progression_snapshot(
        xp=updated_xp,
        completed_levels=completed_levels,
        total_levels=current.get("total_levels", 5),
        readiness=readiness,
        streak=current.get("streak", 0),
        badges=current.get("badges", []),
        transactions=transactions,
    )


def sync_user_progress_state(user_id):
    user_id = str(user_id)
    db = __import__("database").db
    stored_progress = get_user_progress(user_id) or {}

    user_transactions = [
        transaction
        for transaction in db.select("xp_transaction") or []
        if str(transaction.get("user_id", "")) == user_id
    ]
    if user_transactions:
        xp_total = max(0, sum(int(transaction.get("xp_amount", 0) or 0) for transaction in user_transactions))
    else:
        xp_total = max(0, int(stored_progress.get("xp", 0) or 0))

    policy_record = get_latest_user_policy(user_id)
    all_learning_completions = []
    for completion in db.select("learning_completion") or []:
        if str(completion.get("user_id", "")) == user_id:
            all_learning_completions.append(completion)
    simulation_completions = get_simulation_completions_for_user(user_id)
    completion_keys = {str(item.get("completion_key")) for item in all_learning_completions if item.get("completion_key")}
    for transaction in user_transactions:
        if str(transaction.get("activity_type", "")) not in {"learning_question_correct", "learning_scenario"}:
            continue
        activity_id = str(transaction.get("activity_id", ""))
        if activity_id and activity_id not in completion_keys and int(transaction.get("xp_amount", 0) or 0) > 0:
            all_learning_completions.append({
                "completion_key": activity_id,
                "completed_at": transaction.get("created_at"),
                "readiness_gain": 0.5,
            })
            completion_keys.add(activity_id)
    readiness_activities = all_learning_completions + simulation_completions
    if readiness_activities:
        readiness = compute_user_readiness(
            has_policy=bool(policy_record),
            learning_completions=readiness_activities,
            total_levels=max(1, len(all_learning_completions) or 5),
        )
    elif policy_record:
        readiness = max(
            int(stored_progress.get("readiness", 0) or 0),
            compute_user_readiness(has_policy=True, learning_completions=[], total_levels=5),
        )
    else:
        readiness = int(stored_progress.get("readiness", 0) or 0)

    completed_levels = len({str(item.get("completion_key", "")) for item in all_learning_completions if item.get("completion_key")})
    if not all_learning_completions:
        completed_levels = int(stored_progress.get("completed_levels", 0) or 0)
    activity_dates = [item.get("completed_at") for item in readiness_activities if item.get("completed_at")]
    activity_dates.extend(item.get("created_at") for item in user_transactions if item.get("created_at"))
    streak = compute_user_streak(activity_dates) if activity_dates else int(stored_progress.get("streak", 0) or 0)
    stored_badges = stored_progress.get("badges") or []
    badge_names = [str(item.get("name", "")) for item in get_badges_for_user(user_id) if item.get("name")]
    if not badge_names:
        badge_names = [str(item.get("name", item)) if isinstance(item, dict) else str(item) for item in stored_badges]
    payload = {
        "user_id": user_id,
        "xp": int(xp_total),
        "streak": int(streak),
        "readiness": int(readiness),
        "completed_levels": int(completed_levels),
        "badges": badge_names,
        "last_activity_date": max((item.get("completed_at") for item in all_learning_completions if item.get("completed_at")), default=None),
        "updated_at": to_surreal_datetime(),
    }
    create_or_update_user_progress(user_id, payload)
    snapshot = calculate_progression_snapshot(
        xp=xp_total,
        completed_levels=completed_levels,
        total_levels=max(1, len(all_learning_completions) or 5),
        readiness=readiness,
        streak=streak,
        badges=badge_names,
        transactions=[],
    )
    snapshot["completed_learning_items"] = [
        str(item.get("completion_key"))
        for item in all_learning_completions
        if item.get("completion_key")
    ]
    return snapshot


def ensure_user_progress_record(user_id):
    current_progress = get_user_progress(str(user_id))
    if current_progress:
        return current_progress
    default = {
        "user_id": str(user_id),
        "xp": 0,
        "streak": 0,
        "readiness": 0,
        "completed_levels": 0,
        "badges": [],
    }
    return create_or_update_user_progress(str(user_id), default)


app = Flask(__name__)
app.config.from_object(Config)
app.config["SECRET_KEY"] = Config.FLASK_SECRET_KEY
app.config["MAX_CONTENT_LENGTH"] = MAX_POLICY_FILE_SIZE
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

oauth = register_oauth(app)
n8n_service = N8NService(app.config)
ai_service = AIService(app.config)


@app.after_request
def add_cors_headers(response):
    origin = request.headers.get("Origin")
    if origin:
        parsed = urlparse(origin)
        if parsed.scheme in {"http", "https"} and parsed.hostname in {"127.0.0.1", "localhost"}:
            response.headers["Access-Control-Allow-Origin"] = origin
        else:
            response.headers["Access-Control-Allow-Origin"] = resolve_frontend_url(request)
    else:
        response.headers["Access-Control-Allow-Origin"] = resolve_frontend_url(request)

    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PATCH, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response


@app.route("/", methods=["GET", "OPTIONS"])
def index():
    if request.method == "OPTIONS":
        return "", 200
    return redirect(resolve_frontend_url(request))


@app.route("/dashboard", methods=["GET", "OPTIONS"])
@login_required
def dashboard():
    if request.method == "OPTIONS":
        return "", 200
    return redirect(resolve_frontend_url(request))


@app.route("/api/session", methods=["GET", "OPTIONS"])
def session_status():
    if request.method == "OPTIONS":
        return "", 200

    user = get_current_user()
    if not user:
        return jsonify({"authenticated": False})

    user_id = str(user.get("id"))
    policy_status = get_policy_status_for_user(user_id)
    policy_record = get_latest_user_policy(user_id)
    learning_record = get_latest_user_learning(user_id)
    progress = sync_user_progress_state(user_id)

    progression = calculate_progression_snapshot(
        xp=int((progress or {}).get("xp", 0) or 0),
        completed_levels=int((progress or {}).get("completed_levels", 0) or 0),
        total_levels=int((progress or {}).get("total_levels", 5) or 5),
        readiness=int((progress or {}).get("readiness", 0) or 0),
        streak=int((progress or {}).get("streak", 0) or 0),
        badges=(progress or {}).get("badges", []) or [],
    )
    progression["completed_learning_items"] = (progress or {}).get("completed_learning_items", [])

    return jsonify(
        {
            "authenticated": True,
            "has_uploaded_policy": policy_status["has_document"],
            "policy_status": policy_status["status"],
            "policy_document_count": policy_status["document_count"],
            "policy_id": str(policy_record.get("id")) if policy_record else None,
            "learning_generation_id": str(learning_record.get("id")) if learning_record else None,
            "user": {
                "id": str(user.get("id")),
                "name": user.get("name"),
                "email": user.get("email"),
                "auth_provider": user.get("auth_provider"),
            },
            "progress": progression,
        }
    )


@app.route("/api/policies/status", methods=["GET", "OPTIONS"])
@login_required
def policy_status():
    if request.method == "OPTIONS":
        return "", 200
    user = get_current_user()
    return jsonify(get_policy_status_for_user(str(user.get("id"))))


@app.route("/api/dashboard", methods=["GET", "OPTIONS"])
@login_required
def dashboard_data():
    if request.method == "OPTIONS":
        return "", 200

    user = get_current_user()
    user_id = str(user.get("id"))
    policy_record = get_latest_user_policy(user_id)
    learning_record = get_latest_user_learning(user_id)
    progress = sync_user_progress_state(user_id)

    policy_payload = policy_record.get("extracted_data") if policy_record else {}
    learning_payload = learning_record.get("learning") if learning_record else {}
    readiness = int(progress.get("readiness", 0) or 0)

    progress_payload = {
        "xp": int(progress.get("xp", 0) or 0),
        "streak": int(progress.get("streak", 0) or 0),
        "readiness": readiness,
        "completed_levels": int(progress.get("completed_levels", 0) or 0),
        "next_milestone_xp": int(progress.get("next_milestone_xp", 100) or 100),
        "learning_percentage": int(progress.get("learning_percentage", 0) or 0),
        "level": int(progress.get("level", 1) or 1),
            "completed_learning_items": progress.get("completed_learning_items", []),
    }

    response = {
        "user": {
            "id": user_id,
            "name": user.get("name"),
            "email": user.get("email"),
        },
        "policy": policy_payload or None,
        "learning": learning_payload or None,
        "progress": progress_payload,
        "stats": {
            "xp": progress_payload["xp"],
            "streak": progress_payload["streak"],
            "readiness": readiness,
            "completed_levels": progress_payload["completed_levels"],
        },
        "policy_id": str(policy_record.get("id")) if policy_record else None,
        "learning_generation_id": str(learning_record.get("id")) if learning_record else None,
    }
    return jsonify(response)


def build_simulation_policy_context(policy_payload):
    return {
        "document": policy_payload.get("document") or {},
        "coverage": policy_payload.get("coverage") or {},
        "financial": policy_payload.get("financial") or {},
        "limits": policy_payload.get("limits") or {},
        "waiting_periods": policy_payload.get("waiting_periods") or [],
        "exclusions": policy_payload.get("exclusions") or [],
        "claim_process": policy_payload.get("claim_process") or {},
        "important_conditions": policy_payload.get("important_conditions") or [],
    }


def build_local_simulation_result(scenario, policy_context):
    scenario_text = scenario.lower()
    coverage = policy_context.get("coverage") or {}
    exclusions = [str(item) for item in policy_context.get("exclusions") or []]
    relevant_exclusion = next((item for item in exclusions if any(word in item.lower() for word in scenario_text.split() if len(word) > 4)), None)
    hospitalization = coverage.get("hospitalization")
    if relevant_exclusion:
        status = "excluded"
        explanation = "The extracted policy lists a relevant exclusion. Review the exact clause before relying on this result."
        basis = [f"Exclusion: {relevant_exclusion}"]
    elif "hospital" in scenario_text or "inpatient" in scenario_text:
        if hospitalization is True:
            status = "covered"
            explanation = "Your extracted policy includes hospitalization coverage, subject to the policy conditions."
            basis = ["Hospitalization is marked as covered in the extracted policy."]
        elif hospitalization is False:
            status = "excluded"
            explanation = "Your extracted policy does not mark hospitalization as covered."
            basis = ["Hospitalization is marked as not covered in the extracted policy."]
        else:
            status = "not_specified"
            explanation = "INSURA couldn't determine hospitalization coverage from the available policy information."
            basis = []
    else:
        status = "not_specified"
        explanation = "INSURA couldn't determine this from the available policy information."
        basis = []

    financial = policy_context.get("financial") or {}
    limits = policy_context.get("limits") or {}
    claim_process = policy_context.get("claim_process") or {}
    waiting_periods = policy_context.get("waiting_periods") or []
    waiting_period = next(
        (
            str(item.get("period"))
            for item in waiting_periods
            if isinstance(item, dict) and item.get("period")
        ),
        "Not specified in your uploaded policy.",
    )
    return {
        "scenario": scenario,
        "coverage_status": status,
        "confidence": "medium" if basis else "low",
        "explanation": explanation,
        "policy_basis": basis,
        "financial_considerations": {
            "deductible": financial.get("deductible") or "Not specified in your uploaded policy.",
            "copay": financial.get("copayment") or "Not specified in your uploaded policy.",
            "limit": next((str(value) for value in limits.values() if value), "Not specified in your uploaded policy."),
            "other_possible_cost": "Not specified in your uploaded policy.",
        },
        "waiting_period": waiting_period,
        "documents": claim_process.get("documents") or [],
        "next_steps": claim_process.get("deadlines") or [],
        "missing_information": [] if basis else ["Relevant coverage terms were not found in the extracted policy."],
        "limits": [f"{key}: {value}" for key, value in limits.items() if value],
        "claim_path": claim_process.get("cashless") or claim_process.get("reimbursement") or [],
    }


@app.route("/api/simulations/analyze", methods=["POST", "OPTIONS"])
@login_required
def analyze_simulation():
    if request.method == "OPTIONS":
        return "", 200

    user = get_current_user()
    scenario = str((request.get_json(silent=True) or {}).get("scenario") or "").strip()
    if not scenario:
        return jsonify({"error": "Describe the situation you want to rehearse."}), 400
    if len(scenario) > 1000:
        return jsonify({"error": "Your situation must be 1,000 characters or fewer."}), 400

    policy_record = get_latest_user_policy(str(user.get("id")))
    if not policy_record:
        return jsonify({"error": "We couldn't find your policy information right now."}), 404

    policy_context = build_simulation_policy_context(policy_record.get("extracted_data") or {})
    try:
        generated = ai_service.analyze_simulation(scenario, policy_context)
        result = normalize_simulation_response(generated, scenario)
    except (AIServiceError, ValueError, SimulationValidationError) as exc:
        app.logger.warning("AI simulation unavailable; using local policy simulation: %s", type(exc).__name__)
        result = build_local_simulation_result(scenario, policy_context)

    simulation_id = uuid.uuid4().hex
    scenario_id = hashlib.sha256(f"{policy_record.get('id')}:{scenario.casefold()}".encode("utf-8")).hexdigest()
    return jsonify({"success": True, "simulation_id": simulation_id, "scenario_id": scenario_id, "policy_id": str(policy_record.get("id")), "result": result, "usage": ai_service.last_usage})


def chat_payload(chat, messages=None):
    payload = {
        "id": str(chat.get("id")),
        "title": str(chat.get("title") or "New chat"),
        "created_at": chat.get("created_at"),
        "updated_at": chat.get("updated_at"),
    }
    if messages is not None:
        payload["messages"] = [
            {"id": str(message.get("id")), "role": message.get("role"), "content": message.get("content"), "created_at": message.get("created_at")}
            for message in messages
        ]
    return payload


def chat_title(question):
    compact = " ".join(question.split())
    return compact if len(compact) <= 48 else f"{compact[:45].rstrip()}..."


@app.route("/api/chats", methods=["GET", "POST", "OPTIONS"])
@login_required
def chats():
    if request.method == "OPTIONS":
        return "", 200
    user_id = str(get_current_user().get("id"))
    if request.method == "GET":
        return jsonify({"success": True, "chats": [chat_payload(chat) for chat in get_chats_for_user(user_id)]})

    title = str((request.get_json(silent=True) or {}).get("title") or "New chat").strip()[:120] or "New chat"
    now = to_surreal_datetime()
    chat = create_chat({"user_id": user_id, "title": title, "created_at": now, "updated_at": now})
    return jsonify({"success": True, "chat": chat_payload(chat)}), 201


@app.route("/api/chats/<chat_id>", methods=["GET", "PATCH", "OPTIONS"])
@login_required
def chat_detail(chat_id):
    if request.method == "OPTIONS":
        return "", 200
    user_id = str(get_current_user().get("id"))
    chat = get_chat_for_user(user_id, chat_id)
    if not chat:
        return jsonify({"error": "Chat not found."}), 404
    if request.method == "PATCH":
        title = str((request.get_json(silent=True) or {}).get("title") or "").strip()
        if not title or len(title) > 120:
            return jsonify({"error": "Chat title must be between 1 and 120 characters."}), 400
        chat = update_chat(chat["id"], {"title": title, "updated_at": to_surreal_datetime()})
    return jsonify({"success": True, "chat": chat_payload(chat, get_chat_messages(chat["id"], user_id))})


@app.route("/api/chats/<chat_id>/messages", methods=["POST", "OPTIONS"])
@login_required
def chat_messages(chat_id):
    if request.method == "OPTIONS":
        return "", 200

    user = get_current_user()
    user_id = str(user.get("id"))
    chat = get_chat_for_user(user_id, chat_id)
    if not chat:
        return jsonify({"error": "Chat not found."}), 404
    question = str((request.get_json(silent=True) or {}).get("content") or "").strip()
    if not question:
        return jsonify({"error": "Ask an insurance question."}), 400
    if len(question) > 1000:
        return jsonify({"error": "Your question must be 1,000 characters or fewer."}), 400

    user_message = create_chat_message({"chat_id": str(chat["id"]), "user_id": user_id, "role": "user", "content": question, "created_at": to_surreal_datetime()})
    if str(chat.get("title") or "New chat") == "New chat":
        chat = update_chat(chat["id"], {"title": chat_title(question), "updated_at": to_surreal_datetime()})
    policy_record = get_latest_user_policy(str(user.get("id")))

    try:
        policy_context = build_simulation_policy_context(policy_record.get("extracted_data") or {}) if policy_record else {}
        if policy_record:
            retrieved_facts = cognee_policy_service.retrieve_policy(
                str(user.get("id")),
                str(policy_record.get("id") or policy_record.get("analysis_id") or ""),
                question,
                policy_record.get("extracted_data") or {},
            )
            if retrieved_facts:
                policy_context = dict(policy_context)
                policy_context["retrieved_policy_facts"] = retrieved_facts
        answer = ai_service.answer_policy_chat(question, policy_context)
    except AIServiceError:
        return jsonify({"error": "INSURA couldn't answer that right now."}), 502
    assistant_message = create_chat_message({"chat_id": str(chat["id"]), "user_id": user_id, "role": "assistant", "content": answer, "created_at": to_surreal_datetime()})
    chat = update_chat(chat["id"], {"updated_at": to_surreal_datetime()})
    return jsonify({"success": True, "chat": chat_payload(chat), "user_message": {"id": str(user_message.get("id")), "role": "user", "content": question, "created_at": user_message.get("created_at")}, "assistant_message": {"id": str(assistant_message.get("id")), "role": "assistant", "content": answer, "created_at": assistant_message.get("created_at")}, "answer": answer, "usage": ai_service.last_usage})


@app.route("/api/chat", methods=["POST", "OPTIONS"])
@login_required
def legacy_policy_chat():
    if request.method == "OPTIONS":
        return "", 200
    return jsonify({"error": "Use the persistent chat endpoints."}), 410


@app.route("/api/sarvam/transcribe", methods=["POST", "OPTIONS"])
@login_required
def sarvam_transcribe():
    if request.method == "OPTIONS":
        return "", 200
    audio = request.files.get("audio")
    if audio is None or not audio.filename:
        return jsonify({"error": "Audio is required."}), 400
    try:
        result = sarvam_service.transcribe(
            audio.stream.read(10 * 1024 * 1024 + 1),
            audio.filename,
            audio.mimetype,
            str(request.form.get("language_code") or "unknown"),
        )
    except SarvamServiceError as exc:
        app.logger.warning("Sarvam transcription unavailable: %s", exc)
        return jsonify({"error": "Voice transcription is unavailable. Text chat is still available."}), 503
    return jsonify({"transcript": result.get("transcript") or "", "language_code": result.get("language_code")})


@app.route("/api/sarvam/translate", methods=["POST", "OPTIONS"])
@login_required
def sarvam_translate():
    if request.method == "OPTIONS":
        return "", 200
    payload = request.get_json(silent=True) or {}
    text = str(payload.get("text") or "").strip()
    source_language_code = str(payload.get("source_language_code") or "en-IN")
    target_language_code = str(payload.get("target_language_code") or "en-IN")
    if not text:
        return jsonify({"error": "Text is required."}), 400
    try:
        result = sarvam_service.translate(text, source_language_code, target_language_code)
    except SarvamServiceError as exc:
        app.logger.warning("Sarvam translation unavailable: %s", exc)
        return jsonify({"error": "Translation is unavailable."}), 503
    return jsonify({"translated_text": result.get("translated_text") or ""})


@app.route("/api/sarvam/speak", methods=["POST", "OPTIONS"])
@login_required
def sarvam_speak():
    if request.method == "OPTIONS":
        return "", 200
    payload = request.get_json(silent=True) or {}
    text = str(payload.get("text") or "").strip()
    target_language_code = str(payload.get("target_language_code") or "en-IN")
    if not text:
        return jsonify({"error": "Text is required."}), 400
    try:
        audio = sarvam_service.synthesize(text, target_language_code)
    except SarvamServiceError as exc:
        app.logger.warning("Sarvam speech synthesis unavailable: %s", exc)
        return jsonify({"error": "Speech playback is unavailable."}), 503
    return send_file(io.BytesIO(audio), mimetype="audio/wav", as_attachment=False, download_name="insura-response.wav")


@app.route("/api/progression", methods=["GET", "POST", "OPTIONS"])
@login_required
def progression_status():
    if request.method == "OPTIONS":
        return "", 200

    user = get_current_user()
    user_id = str(user.get("id"))
    progress = sync_user_progress_state(user_id)
    if request.method == "POST":
        payload = request.get_json(silent=True) or {}
        activity_type = str(payload.get("activity_type") or "").strip()
        activity_id = str(payload.get("activity_id") or "").strip()
        if not activity_type or not activity_id:
            return jsonify({"error": "activity_type and activity_id are required."}), 400

        if find_xp_transaction(user_id, activity_type, activity_id):
            snapshot = sync_user_progress_state(user_id)
            return jsonify({"success": True, "progress": snapshot, "awarded": False, "duplicate": True})

        xp_award = PROGRESSION_XP_AWARDS.get(activity_type, 0)

        if xp_award:
            if activity_type in {"learning_question_correct", "learning_scenario"}:
                existing_completion = find_learning_completion(user_id, activity_id)
                if existing_completion:
                    snapshot = sync_user_progress_state(user_id)
                    return jsonify({"success": True, "progress": snapshot, "awarded": False, "duplicate": True, "already_completed": True})
                policy_record = get_latest_user_policy(user_id)
                try:
                    create_learning_completion({
                        "user_id": user_id,
                        "policy_id": str(policy_record.get("id")) if policy_record else None,
                        "learning_id": str(payload.get("learning_id") or ""),
                        "completion_key": activity_id,
                        "xp_awarded": xp_award,
                    })
                except RuntimeError:
                    app.logger.exception("Could not persist learning completion")
                    return jsonify({"error": "Learning completion could not be saved."}), 500
            if activity_type == "simulation_completion":
                simulation_payload = payload.get("simulation") if isinstance(payload.get("simulation"), dict) else {}
                create_simulation_completion({
                    "user_id": user_id,
                    "simulation_id": str(simulation_payload.get("simulation_id") or activity_id),
                    "scenario_id": activity_id,
                    "completed_steps": int(payload.get("completed_steps", 6) or 0),
                    "xp_awarded": xp_award,
                    "readiness_gain": 0.5,
                    "result": simulation_payload.get("result") or {},
                })
            create_xp_transaction({
                "user_id": user_id,
                "activity_type": activity_type,
                "activity_id": activity_id,
                "xp_amount": xp_award,
                "reason": f"{activity_type} completion",
            })

        snapshot = sync_user_progress_state(user_id)
        return jsonify({"success": True, "progress": snapshot, "awarded": bool(xp_award), "duplicate": False})

    return jsonify({"success": True, "progress": progress})


@app.route("/api/passport", methods=["GET", "OPTIONS"])
@login_required
def passport_data():
    if request.method == "OPTIONS":
        return "", 200

    user = get_current_user()
    user_id = str(user.get("id"))
    policy_record = get_latest_user_policy(user_id)
    policy_payload = (policy_record or {}).get("extracted_data") or {}
    document = policy_payload.get("document") or {}
    coverage = policy_payload.get("coverage") or {}
    financial = policy_payload.get("financial") or {}
    progress = get_user_progress(user_id) or {}

    passport = {
        "passport_id": f"INSURA-{user_id[:8].upper()}",
        "name": user.get("name"),
        "email": user.get("email"),
        "product_name": document.get("product_name") or "Health Insurance",
        "insurer": document.get("insurer") or "Insurer not captured",
        "policy_number": document.get("uin") or "Not available",
        "coverage": coverage.get("sum_insured_options", ["Not specified"])[0] if coverage.get("sum_insured_options") else "Not specified",
        "premium": financial.get("premium_tables") or "Check policy schedule",
        "valid_until": "Policy term details pending",
        "status": "ACTIVE",
        "readiness": int(progress.get("readiness", 0) or calculate_readiness(policy_payload, {}, progress)),
    }
    return jsonify({"passport": passport})


def get_or_create_policy_share(user_id, policy_record):
    policy_id = str(policy_record.get("id") or "")
    existing = get_policy_share_for_user(user_id, policy_id)
    if existing:
        return existing
    return create_policy_share({
        "user_id": str(user_id),
        "policy_id": policy_id,
        "share_token": secrets.token_urlsafe(32),
        "created_at": to_surreal_datetime(),
        "active": True,
    })


def sanitize_policy_share(policy_payload):
    document = policy_payload.get("document") or {}
    coverage = policy_payload.get("coverage") or {}
    financial = policy_payload.get("financial") or {}
    limits = policy_payload.get("limits") or {}
    waiting_periods = policy_payload.get("waiting_periods") or []
    claim_process = policy_payload.get("claim_process") or {}

    def safe_text(value):
        if value is None or value == "":
            return "Not specified"
        return str(value).replace("₹", "INR ").replace("\u2013", "-").replace("\u2014", "-")

    def safe_list(value):
        if isinstance(value, list):
            return [safe_text(item) for item in value if item not in (None, "")]
        return [safe_text(value)] if value not in (None, "") else []

    premium_tables = financial.get("premium_tables")
    premium = safe_list(premium_tables) if premium_tables else []
    waiting = []
    for item in waiting_periods:
        if isinstance(item, dict):
            waiting.append(f"{safe_text(item.get('condition') or 'Specified treatment')}: {safe_text(item.get('period'))}")
        else:
            waiting.append(safe_text(item))
    benefits = []
    for key, label in (("hospitalization", "Hospitalization"), ("day_care", "Day-care procedures"), ("domiciliary", "Domiciliary care"), ("ambulance", "Ambulance")):
        if key in coverage:
            benefits.append(f"{label}: {safe_text(coverage.get(key))}")
    return {
        "policy_type": safe_text(document.get("product_name") or document.get("document_type")),
        "insurer": safe_text(document.get("insurer")),
        "coverage_amount": safe_list(coverage.get("sum_insured_options")),
        "premium": premium,
        "validity": safe_text(document.get("validity") or document.get("policy_term")),
        "deductible": safe_text(financial.get("deductible")),
        "copay": safe_text(financial.get("copayment")),
        "waiting_periods": waiting,
        "benefits": benefits,
        "exclusions": safe_list(policy_payload.get("exclusions")),
        "limits": [f"{safe_text(key)}: {safe_text(value)}" for key, value in limits.items() if value not in (None, "")],
        "claim_documents": safe_list(claim_process.get("documents")),
        "claim_deadlines": safe_list(claim_process.get("deadlines")),
    }


def build_policy_summary_pdf(summary):
    buffer = io.BytesIO()
    document = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=18 * mm, leftMargin=18 * mm, topMargin=16 * mm, bottomMargin=16 * mm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("InsuraTitle", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=18, textColor="#102846", spaceAfter=12)
    heading_style = ParagraphStyle("InsuraHeading", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=11, textColor="#16718a", spaceBefore=9, spaceAfter=5)
    body_style = ParagraphStyle("InsuraBody", parent=styles["BodyText"], fontName="Helvetica", fontSize=9, leading=13, textColor="#26384d")
    story = [Paragraph("INSURA POLICY SUMMARY", title_style), Paragraph("A structured summary of the available policy information", body_style), Spacer(1, 8)]
    sections = [
        ("Policy details", [("Policy Type", summary["policy_type"]), ("Insurer", summary["insurer"]), ("Coverage Amount", "; ".join(summary["coverage_amount"]) or "Not specified"), ("Premium", "; ".join(summary["premium"]) or "Not specified"), ("Policy Validity", summary["validity"])]),
        ("Financial terms", [("Deductible", summary["deductible"]), ("Co-pay", summary["copay"])]),
    ]
    for heading, rows in sections:
        story.append(Paragraph(heading, heading_style))
        table = Table([[Paragraph(f"<b>{html.escape(label)}</b>", body_style), Paragraph(html.escape(value), body_style)] for label, value in rows], colWidths=[42 * mm, 128 * mm])
        table.setStyle(TableStyle([("BACKGROUND", (0, 0), (0, -1), "#edf5f7"), ("GRID", (0, 0), (-1, -1), 0.3, "#c8d9df"), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("PADDING", (0, 0), (-1, -1), 6)]))
        story.append(table)
    list_sections = [("Waiting periods", summary["waiting_periods"]), ("Coverage / Benefits", summary["benefits"]), ("Major exclusions", summary["exclusions"]), ("Important limits", summary["limits"]), ("Claim documentation", summary["claim_documents"] + summary["claim_deadlines"])]
    for heading, items in list_sections:
        story.append(Paragraph(heading, heading_style))
        story.append(Paragraph("<br/>".join(f"- {html.escape(item)}" for item in items) if items else "Not specified", body_style))
    story.extend([Spacer(1, 14), Paragraph("DISCLAIMER", heading_style), Paragraph("This document is a policy summary generated from the information available in the user's uploaded policy. It is not a replacement for the original policy document. Final claim decisions are subject to the insurer's policy terms and assessment.", body_style)])
    document.build(story)
    buffer.seek(0)
    return buffer


def _comparison_label(value):
    labels = {
        "copay": "Co-pay",
        "coverage": "Coverage",
        "deductible": "Deductible",
        "exclusions": "Exclusions",
        "financial": "Financial terms",
        "important_conditions": "Important conditions",
        "limits": "Limits",
        "premium": "Premium",
        "waiting_periods": "Waiting periods",
    }
    text = str(value or "").strip().replace("_", " ")
    return labels.get(text.lower(), text.title() or "Policy detail")


def _comparison_value(value):
    if value is None or value == "":
        return "Not specified"
    if isinstance(value, bool):
        return "Yes" if value else "No"
    if isinstance(value, dict):
        parts = []
        for key, item in value.items():
            parts.append(f"{_comparison_label(key)}: {_comparison_value(item)}")
        return "; ".join(parts) or "Not specified"
    if isinstance(value, (list, tuple, set)):
        parts = [_comparison_value(item) for item in value]
        return "; ".join(item for item in parts if item != "Not specified") or "Not specified"
    if isinstance(value, str):
        stripped = value.strip()
        if stripped[:1] in {"{", "["} and stripped[-1:] in {"}", "]"}:
            try:
                return _comparison_value(json.loads(stripped))
            except (TypeError, ValueError, json.JSONDecodeError):
                try:
                    return _comparison_value(ast.literal_eval(stripped))
                except (ValueError, SyntaxError):
                    pass
    return str(value).replace("₹", "INR ").replace("\u2013", "-").replace("\u2014", "-")


def _comparison_change_type(old_value, new_value, change_type=None):
    requested = str(change_type or "").strip().lower()
    if requested in {"added", "removed", "changed", "unchanged"}:
        return requested.title()
    old_missing = old_value in (None, "", {}, [])
    new_missing = new_value in (None, "", {}, [])
    if old_missing and not new_missing:
        return "Added"
    if new_missing and not old_missing:
        return "Removed"
    return "Unchanged" if old_value == new_value else "Changed"


def _comparison_section(field):
    name = str(field or "").lower()
    if "premium" in name or "cost" in name or name == "financial":
        return "Premium & Cost"
    if "deduct" in name or "copay" in name or "co-pay" in name:
        return "Deductible & Co-pay"
    if "wait" in name:
        return "Waiting Periods"
    if "exclusion" in name:
        return "Exclusions"
    if "limit" in name:
        return "Limits"
    if "condition" in name:
        return "Important Conditions"
    if "coverage" in name or "benefit" in name:
        return "Coverage & Benefits"
    return "Other Changes"


def build_comparison_pdf(comparison, old_name, renewed_name):
    buffer = io.BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=18 * mm,
        title="INSURA Policy Comparison",
    )
    styles = getSampleStyleSheet()
    title = ParagraphStyle("ComparisonTitle", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=18, leading=22, textColor="#102846", spaceAfter=10)
    heading = ParagraphStyle("ComparisonHeading", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=11, leading=14, textColor="#16718a", spaceBefore=10, spaceAfter=5)
    body = ParagraphStyle("ComparisonBody", parent=styles["BodyText"], fontName="Helvetica", fontSize=8.5, leading=11, textColor="#26384d")
    small = ParagraphStyle("ComparisonSmall", parent=body, fontSize=8, leading=10)
    table_header = ParagraphStyle("ComparisonTableHeader", parent=body, fontName="Helvetica-Bold", textColor=colors.white)

    def cell(value, style=body):
        return Paragraph(html.escape(_comparison_value(value)).replace("; ", ";<br/>"), style)

    def comparison_rows(changes):
        rows = []
        for change in changes:
            if not isinstance(change, dict):
                continue
            old_value = change.get("old_value")
            new_value = change.get("new_value")
            rows.append([
                cell(_comparison_label(change.get("field"))),
                cell(old_value),
                cell(new_value),
                cell(_comparison_change_type(old_value, new_value, change.get("change_type"))),
            ])
        return rows

    def comparison_table(rows):
        table = Table(
            [[Paragraph("Item", table_header), Paragraph("Old Policy", table_header), Paragraph("Renewed Policy", table_header), Paragraph("Change", table_header)]] + rows,
            colWidths=[36 * mm, 48 * mm, 66 * mm, 30 * mm],
            repeatRows=1,
            hAlign="LEFT",
        )
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), "#16718a"),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), ["#f4f8f9", colors.white]),
            ("GRID", (0, 0), (-1, -1), 0.35, "#c8d9df"),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        return table

    raw_changes = comparison.get("changes", []) if isinstance(comparison, dict) else []
    changes = [change for change in raw_changes if isinstance(change, dict)]
    grouped = {section: [] for section in (
        "Coverage & Benefits", "Premium & Cost", "Limits", "Deductible & Co-pay",
        "Waiting Periods", "Exclusions", "Important Conditions", "Other Changes",
    )}
    for change in changes:
        grouped[_comparison_section(change.get("field"))].append(change)

    story = [
        Paragraph("INSURA POLICY COMPARISON", title),
        Paragraph(f"<b>Old Policy:</b> {html.escape(_comparison_value(old_name))}<br/><b>Renewed Policy:</b> {html.escape(_comparison_value(renewed_name))}", body),
        Spacer(1, 8),
        Paragraph("Comparison Summary", heading),
    ]
    summary_rows = comparison_rows(changes)
    story.append(comparison_table(summary_rows or [[cell("Policy details"), cell(None), cell(None), cell("Unchanged")]]))

    key_changes = [change for change in changes if _comparison_change_type(change.get("old_value"), change.get("new_value"), change.get("change_type")) != "Unchanged"]
    story.append(Paragraph("Key Changes", heading))
    if key_changes:
        for change in key_changes[:5]:
            label = _comparison_label(change.get("field"))
            old_value = _comparison_value(change.get("old_value"))
            new_value = _comparison_value(change.get("new_value"))
            story.append(Paragraph(f"&#8226; <b>{html.escape(label)}:</b> {html.escape(old_value)} -&gt; {html.escape(new_value)} ({html.escape(_comparison_change_type(change.get('old_value'), change.get('new_value'), change.get('change_type')))})", body))
    else:
        story.append(Paragraph("No material changes were identified.", body))

    for section, section_changes in grouped.items():
        story.append(Paragraph(section, heading))
        story.append(comparison_table(comparison_rows(section_changes) or [[cell("No details available"), cell(None), cell(None), cell("Unchanged")]]))

    story.extend([
        Spacer(1, 12),
        Paragraph("Disclaimer", heading),
        Paragraph("This comparison is generated from stored policy analysis and is not an insurer decision.", small),
    ])

    def add_page_number(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#607080"))
        canvas.drawRightString(A4[0] - 15 * mm, 9 * mm, f"Page {doc.page}")
        canvas.restoreState()

    document.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
    buffer.seek(0)
    return buffer.getvalue()


def build_local_policy_comparison(old_payload, renewed_payload):
    fields = {
        "coverage": (old_payload.get("coverage"), renewed_payload.get("coverage")),
        "financial": (old_payload.get("financial"), renewed_payload.get("financial")),
        "validity": ((old_payload.get("document") or {}).get("validity"), (renewed_payload.get("document") or {}).get("validity")),
        "limits": (old_payload.get("limits"), renewed_payload.get("limits")),
        "exclusions": (old_payload.get("exclusions"), renewed_payload.get("exclusions")),
        "waiting_periods": (old_payload.get("waiting_periods"), renewed_payload.get("waiting_periods")),
        "benefits": ((old_payload.get("coverage") or {}).get("benefits"), (renewed_payload.get("coverage") or {}).get("benefits")),
        "important_conditions": (old_payload.get("important_conditions"), renewed_payload.get("important_conditions")),
    }
    changes = []
    for field, (old_value, new_value) in fields.items():
        if old_value != new_value:
            changes.append({"field": field, "old_value": str(old_value or "Not specified"), "new_value": str(new_value or "Not specified"), "change_type": "changed", "importance": "review", "explanation": "This field differs between the stored policy extractions."})
    return {"summary": "Comparison generated from the stored policy extractions.", "changes": changes}


@app.route("/api/passport/qr", methods=["GET", "OPTIONS"])
@login_required
def passport_qr():
    if request.method == "OPTIONS":
        return "", 200

    user = get_current_user()
    policy_record = get_latest_user_policy(str(user.get("id")))
    if not policy_record:
        return jsonify({"error": "Upload a policy before creating a share QR."}), 404
    share = get_or_create_policy_share(str(user.get("id")), policy_record)
    share_url = f"{resolve_backend_url(request)}/policy/share/{share.get('share_token')}"

    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(share_url)
    qr.make(fit=True)
    image = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    return app.response_class(buffer.getvalue(), mimetype="image/png")


@app.route("/policy/share/<share_token>", methods=["GET"])
def public_policy_share(share_token):
    share = get_policy_share_by_token(share_token)
    if not share:
        return jsonify({"error": "This policy share link is invalid or inactive."}), 404
    policy_record = get_policy_analysis_by_record_id(share.get("policy_id"))
    if not policy_record or str(policy_record.get("user_id", "")) != str(share.get("user_id", "")):
        return jsonify({"error": "This policy share is unavailable."}), 404
    pdf = build_policy_summary_pdf(sanitize_policy_share(policy_record.get("extracted_data") or {}))
    return send_file(pdf, mimetype="application/pdf", as_attachment=False, download_name="insura-policy-summary.pdf")


@app.route("/api/learning/<learning_id>", methods=["GET", "OPTIONS"])
@login_required
def learning_record_for_id(learning_id):
    if request.method == "OPTIONS":
        return "", 200

    user = get_current_user()
    user_id = str(user.get("id"))
    record = None
    for item in get_user_learning_records(user_id):
        if str(item.get("id")) == str(learning_id):
            record = item
            break

    if not record:
        return jsonify({"error": "Learning record not found."}), 404

    return jsonify({"learning": record.get("learning") or {}})


@app.route("/api/learning/progress", methods=["GET", "OPTIONS"])
@login_required
def learning_progress_status():
    if request.method == "OPTIONS":
        return "", 200
    user = get_current_user()
    progress = sync_user_progress_state(str(user.get("id")))
    return jsonify({
        "completed_items": progress.get("completed_learning_items", []),
        "learning_percentage": progress.get("learning_percentage", 0),
        "progress": progress,
    })


@app.route("/register", methods=["POST", "OPTIONS"])
def register():
    if request.method == "OPTIONS":
        return "", 200

    data = request.get_json(silent=True) or request.form or {}
    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))

    if not name:
        return jsonify({"error": "Full name is required."}), 400
    if not email or not EMAIL_RE.fullmatch(email):
        return jsonify({"error": "Please enter a valid email address."}), 400
    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters long."}), 400
    if find_user_by_email(email):
        return jsonify({"error": "An account with this email already exists."}), 409

    user = create_user(
        {
            "name": name,
            "email": email,
            "password_hash": generate_password_hash(password),
            "auth_provider": "local",
            "email_verified": False,
        }
    )

    login_user(user)
    return jsonify({"success": True, "message": "Registration successful.", "user": {"name": name, "email": email}}), 201


@app.route("/login", methods=["POST", "OPTIONS"])
def login():
    if request.method == "OPTIONS":
        return "", 200

    data = request.get_json(silent=True) or request.form or {}
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))

    if not email or not password:
        return jsonify({"error": "Email and password are required."}), 400

    user = find_user_by_email(email)
    if not user or not user.get("password_hash"):
        return jsonify({"error": "Invalid email or password."}), 401

    if not check_password_hash(user["password_hash"], password):
        return jsonify({"error": "Invalid email or password."}), 401

    login_user(user)
    return jsonify({"success": True, "message": "Signed in successfully.", "user": {"name": user.get("name"), "email": email}})


@app.route("/logout", methods=["GET", "POST", "OPTIONS"])
def logout():
    if request.method == "OPTIONS":
        return "", 200

    logout_user()
    return redirect(resolve_frontend_url(request))


@app.route("/api/policy/upload", methods=["POST", "OPTIONS"])
def upload_policy_document():
    if request.method == "OPTIONS":
        return "", 200

    return analyze_policy()

    user = get_current_user()
    if not user:
        return jsonify({"error": "Please sign in first."}), 401

    uploaded_file = request.files.get("file")
    if uploaded_file is None or not uploaded_file.filename:
        return jsonify({"error": "No policy document selected."}), 400

    filename = secure_filename(uploaded_file.filename)
    if not filename.lower().endswith(".pdf"):
        return jsonify({"error": "Please upload a PDF policy document."}), 400

    user_id = str(user.get("id") or "anonymous")
    unique_name = f"{secure_filename(user_id)}_{uuid.uuid4().hex}_{filename}"
    storage_path = os.path.join(UPLOAD_FOLDER, unique_name)
    uploaded_file.save(storage_path)

    webhook_status = "not-configured"
    if app.config.get("N8N_POLICY_INTELLIGENCE_URL"):
        try:
            n8n_service.run_policy_intelligence(
                file_path=storage_path,
                filename=filename,
                user_email=str(user.get("email") or ""),
                user_name=str(user.get("name") or ""),
            )
            webhook_status = "sent"
        except (N8NServiceError, OSError) as exc:
            webhook_status = f"failed:{exc}"

    return jsonify(
        {
            "success": True,
            "message": "Policy document uploaded successfully.",
            "file_name": filename,
            "stored_path": storage_path,
            "webhook_status": webhook_status,
        }
    )


@app.route("/api/policies/analyze", methods=["POST", "OPTIONS"])
def analyze_policy():
    if request.method == "OPTIONS":
        return "", 200

    user = get_current_user()
    if not user:
        return jsonify({"error": "Please sign in first."}), 401

    uploaded_file = request.files.get("policy") or request.files.get("file")
    if uploaded_file is None or not uploaded_file.filename:
        return jsonify({"error": "No policy document selected."}), 400

    filename = secure_filename(uploaded_file.filename)
    if not filename.lower().endswith(".pdf"):
        return jsonify({"error": "Please upload a PDF policy document."}), 400

    file_content = uploaded_file.stream.read(MAX_POLICY_FILE_SIZE + 1)
    if len(file_content) > MAX_POLICY_FILE_SIZE:
        return jsonify({"error": "Policy document must be 20 MB or smaller."}), 413
    if not file_content.startswith(b"%PDF-"):
        return jsonify({"error": "The uploaded file is not a valid PDF document."}), 400

    user_id = str(user.get("id"))
    document_hash = compute_document_hash(file_content)
    existing_document = find_policy_document_by_hash(user_id, document_hash)
    if existing_document:
        storage_path = os.path.join(UPLOAD_FOLDER, f"{secure_filename(user_id)}_{document_hash}_{filename}")
        if not os.path.isfile(storage_path):
            with open(storage_path, "wb") as stored_file:
                stored_file.write(file_content)
        __import__("database").db.merge(existing_document["id"], {"storage_path": storage_path, "file_data": base64.b64encode(file_content).decode("ascii"), "mime_type": "application/pdf", "updated_at": to_surreal_datetime()})
        policy_record = resolve_deduplicated_policy_record(user_id, document_hash)
        if policy_record:
            cognee_policy_service.index_policy(
                user_id,
                str(policy_record.get("id") or policy_record.get("analysis_id") or ""),
                policy_record.get("extracted_data") or {},
            )
            sync_user_progress_state(user_id)
            return jsonify({
                "success": True,
                "policy_id": str(policy_record.get("id")),
                "analysis_id": str(policy_record.get("analysis_id") or policy_record.get("id")),
                "output": policy_record.get("extracted_data") or {},
                "deduplicated": True,
                "message": "This policy has already been processed for this user.",
            })

    stored_filename = f"{secure_filename(user_id)}_{document_hash}_{filename}"
    storage_path = os.path.join(UPLOAD_FOLDER, stored_filename)
    with open(storage_path, "wb") as stored_file:
        stored_file.write(file_content)

    try:
        analysis = n8n_service.run_policy_intelligence(
            filename=filename,
            file_content=file_content,
            user_email=str(user.get("email") or ""),
            user_name=str(user.get("name") or ""),
        )
    except (N8NServiceError, OSError, ValueError) as exc:
        app.logger.error("Policy intelligence request failed: %s", type(exc).__name__)
        return jsonify({"error": "Policy analysis is temporarily unavailable."}), 502

    try:
        policy_intelligence = normalize_policy_intelligence_response(analysis)
    except PolicyIntelligenceValidationError as exc:
        app.logger.error("Policy intelligence response validation failed: %s", exc)
        return jsonify({"error": "Policy analysis returned an invalid result."}), 502

    analysis_id = uuid.uuid4().hex
    try:
        saved_record = create_policy_analysis(
            {
                "user_id": user_id,
                "file_name": filename,
                "analysis_id": analysis_id,
                "extracted_data": policy_intelligence,
            }
        )
    except RuntimeError:
        app.logger.exception("Could not save policy analysis for authenticated user")
        return jsonify({"error": "Policy analysis could not be saved."}), 500

    try:
        create_policy_document(
            {
                "user_id": user_id,
                "file_name": filename,
                "document_hash": document_hash,
                "status": "processed",
                "processing_status": "done",
                "policy_id": str(saved_record.get("analysis_id")) if isinstance(saved_record, dict) else analysis_id,
                "storage_path": storage_path,
                "file_data": base64.b64encode(file_content).decode("ascii"),
                "mime_type": "application/pdf",
            }
        )
    except RuntimeError:
        app.logger.exception("Could not save policy document hash for deduplication")
        return jsonify({"error": "Policy analysis was completed but could not be persisted."}), 500

    cognee_policy_service.index_policy(user_id, str(saved_record.get("id") or analysis_id), policy_intelligence)
    sync_user_progress_state(user_id)
    return jsonify(
        {
            "success": True,
            "policy_id": str(saved_record.get("id")) if isinstance(saved_record, dict) else None,
            "analysis_id": analysis_id,
            "output": policy_intelligence,
            "deduplicated": False,
            "message": "Policy uploaded and readiness initialized.",
        }
    )


def user_table_records(table, user_id):
    return [record for record in (__import__("database").db.select(table) or []) if str(record.get("user_id", "")) == str(user_id)]


@app.route("/api/documents", methods=["GET", "OPTIONS"])
@login_required
def documents_for_user():
    if request.method == "OPTIONS":
        return "", 200
    user_id = str(get_current_user().get("id"))
    documents = get_policy_documents_for_user(user_id)
    return jsonify({"documents": [{"id": str(item.get("id")), "file_name": item.get("file_name"), "status": item.get("processing_status") or item.get("status"), "policy_id": item.get("policy_id"), "created_at": item.get("created_at"), "storage_available": bool(item.get("file_data") or (item.get("storage_path") and os.path.isfile(item.get("storage_path"))))} for item in documents]})


@app.route("/api/documents/<document_id>/download", methods=["GET", "OPTIONS"])
@login_required
def download_document(document_id):
    if request.method == "OPTIONS":
        return "", 200
    user_id = str(get_current_user().get("id"))
    document_id = unquote(str(document_id))
    if not document_id.startswith("policy_document:"):
        return jsonify({"error": "Invalid document identifier."}), 400
    try:
        document, file_bytes = read_policy_document_bytes(user_id, document_id)
    except FileNotFoundError:
        app.logger.error("Original document binary is unavailable: %s", document_id)
        return jsonify({"error": "The original document binary is unavailable in persistent storage."}), 404
    except ValueError:
        app.logger.exception("Stored document data is corrupt: %s", document_id)
        return jsonify({"error": "The stored document data is corrupt."}), 422
    return send_file(io.BytesIO(file_bytes), mimetype=document.get("mime_type") or "application/pdf", as_attachment=True, download_name=secure_filename(document.get("file_name") or "policy.pdf"))


@app.route("/api/policy-comparisons", methods=["GET", "OPTIONS"])
@login_required
def comparisons_for_user():
    if request.method == "OPTIONS":
        return "", 200
    records = user_table_records("policy_comparison", str(get_current_user().get("id")))
    records.sort(key=lambda item: str(item.get("created_at") or ""), reverse=True)
    return jsonify({"comparisons": [{"id": str(item.get("id")), "comparison_id": item.get("comparison_id"), "old_file_name": item.get("old_file_name"), "renewed_file_name": item.get("renewed_file_name"), "comparison": item.get("comparison"), "created_at": item.get("created_at")} for item in records]})


@app.route("/api/reminders", methods=["GET", "POST", "OPTIONS"])
@login_required
def reminders_api():
    if request.method == "OPTIONS":
        return "", 200
    user_id = str(get_current_user().get("id"))
    if request.method == "GET":
        records = user_table_records("reminder", user_id)
        records.sort(key=lambda item: str(item.get("due_at") or ""))
        return jsonify({"reminders": records})
    payload = request.get_json(silent=True) or {}
    title = str(payload.get("title") or "").strip()
    due_at = str(payload.get("due_at") or "").strip()
    if not title or not due_at:
        return jsonify({"error": "title and due_at are required."}), 400
    record = __import__("database").db.create("reminder", {"user_id": user_id, "title": title[:160], "reminder_type": str(payload.get("reminder_type") or "other")[:40], "due_at": to_surreal_datetime(due_at), "notes": str(payload.get("notes") or "")[:500], "created_at": to_surreal_datetime(), "updated_at": to_surreal_datetime(), "status": "open"})
    return jsonify({"reminder": record}), 201


@app.route("/api/reminders/<reminder_id>", methods=["PATCH", "DELETE", "OPTIONS"])
@login_required
def reminder_detail(reminder_id):
    if request.method == "OPTIONS":
        return "", 200
    user_id = str(get_current_user().get("id"))
    record = next((item for item in user_table_records("reminder", user_id) if str(item.get("id")) == str(reminder_id)), None)
    if not record:
        return jsonify({"error": "Reminder not found."}), 404
    if request.method == "DELETE":
        __import__("database").db.delete(record["id"])
        return jsonify({"success": True})
    payload = request.get_json(silent=True) or {}
    changes = {key: payload[key] for key in ("title", "reminder_type", "notes", "status") if key in payload}
    if "due_at" in payload: changes["due_at"] = to_surreal_datetime(payload["due_at"])
    changes["updated_at"] = to_surreal_datetime()
    updated = __import__("database").db.merge(record["id"], changes)
    return jsonify({"reminder": updated})


@app.route("/api/support/tickets", methods=["GET", "POST", "OPTIONS"])
@login_required
def support_tickets_api():
    if request.method == "OPTIONS": return "", 200
    user_id = str(get_current_user().get("id"))
    if request.method == "GET": return jsonify({"tickets": user_table_records("support_ticket", user_id)})
    payload = request.get_json(silent=True) or {}
    subject, message = str(payload.get("subject") or "").strip(), str(payload.get("message") or "").strip()
    if not subject or not message: return jsonify({"error": "subject and message are required."}), 400
    ticket = __import__("database").db.create("support_ticket", {"user_id": user_id, "subject": subject[:160], "message": message[:4000], "status": "open", "created_at": to_surreal_datetime()})
    return jsonify({"ticket": ticket}), 201


@app.route("/api/claims", methods=["GET", "POST", "OPTIONS"])
@login_required
def claims_api():
    if request.method == "OPTIONS": return "", 200
    user_id = str(get_current_user().get("id"))
    if request.method == "GET": return jsonify({"claims": user_table_records("claim", user_id)})
    policy = get_latest_user_policy(user_id)
    if not policy: return jsonify({"error": "Upload a policy before starting a claim."}), 404
    payload = request.get_json(silent=True) or {}
    details = str(payload.get("details") or "").strip()
    if not details: return jsonify({"error": "Claim details are required."}), 400
    claim = __import__("database").db.create("claim", {"user_id": user_id, "policy_id": str(policy.get("id")), "details": details[:5000], "status": "draft", "created_at": to_surreal_datetime(), "updated_at": to_surreal_datetime()})
    return jsonify({"claim": claim, "policy_guidance": (policy.get("extracted_data") or {}).get("claim_process") or {}}), 201


@app.route("/api/settings", methods=["GET", "PATCH", "OPTIONS"])
@login_required
def settings_api():
    if request.method == "OPTIONS": return "", 200
    user_id = str(get_current_user().get("id"))
    records = user_table_records("user_setting", user_id)
    current = records[0] if records else {"settings": {}}
    if request.method == "PATCH":
        settings = request.get_json(silent=True) or {}
        current = __import__("database").db.merge(current["id"], {"settings": settings, "updated_at": to_surreal_datetime()}) if current.get("id") else __import__("database").db.create("user_setting", {"user_id": user_id, "settings": settings, "updated_at": to_surreal_datetime()})
    return jsonify({"settings": current.get("settings") or {}})


@app.route("/api/policies/compare", methods=["POST", "OPTIONS"])
def compare_policies():
    if request.method == "OPTIONS":
        return "", 200

    user = get_current_user()
    if not user:
        return jsonify({"error": "Please sign in first."}), 401

    old_policy = request.files.get("old_policy")
    renewed_policy = request.files.get("renewed_policy")
    old_document_id = str(request.form.get("old_document_id") or "")
    renewed_document_id = str(request.form.get("renewed_document_id") or "")
    stored_documents = None
    if old_document_id and renewed_document_id:
        try:
            old_document, old_file_content = read_policy_document_bytes(str(user.get("id")), unquote(old_document_id))
            renewed_document, renewed_file_content = read_policy_document_bytes(str(user.get("id")), unquote(renewed_document_id))
            stored_documents = (old_document, renewed_document)
        except FileNotFoundError:
            return jsonify({"error": "One or both selected document binaries are unavailable in persistent storage."}), 404
        except ValueError:
            return jsonify({"error": "One or both selected document binaries are corrupt."}), 422
    if stored_documents is None and (old_policy is None or not old_policy.filename):
        return jsonify({"error": "Old policy document is required."}), 400
    if stored_documents is None and (renewed_policy is None or not renewed_policy.filename):
        return jsonify({"error": "Renewed policy document is required."}), 400

    old_filename = secure_filename(stored_documents[0].get("file_name")) if stored_documents else secure_filename(old_policy.filename)
    renewed_filename = secure_filename(stored_documents[1].get("file_name")) if stored_documents else secure_filename(renewed_policy.filename)
    if not old_filename.lower().endswith(".pdf"):
        return jsonify({"error": "Old policy document must be a PDF."}), 400
    if not renewed_filename.lower().endswith(".pdf"):
        return jsonify({"error": "Renewed policy document must be a PDF."}), 400

    if stored_documents is None:
        old_file_content = old_policy.stream.read(MAX_POLICY_FILE_SIZE + 1)
        renewed_file_content = renewed_policy.stream.read(MAX_POLICY_FILE_SIZE + 1)
    if len(old_file_content) > MAX_POLICY_FILE_SIZE or len(renewed_file_content) > MAX_POLICY_FILE_SIZE:
        return jsonify({"error": "Each policy document must be 20 MB or smaller."}), 413
    if not old_file_content.startswith(b"%PDF-") or not renewed_file_content.startswith(b"%PDF-"):
        return jsonify({"error": "Both policy documents must be valid PDF files."}), 400

    try:
        comparison = n8n_service.run_policy_comparison(
            old_filename=old_filename,
            old_file_content=old_file_content,
            renewed_filename=renewed_filename,
            renewed_file_content=renewed_file_content,
        )
    except (N8NServiceError, OSError, ValueError) as exc:
        app.logger.warning("Falling back to stored policy comparison: %s", type(exc).__name__)
        old_record = __import__("database").db.select(old_document_id) if old_document_id else None
        renewed_record = __import__("database").db.select(renewed_document_id) if renewed_document_id else None
        old_record = old_record[0] if isinstance(old_record, list) and old_record else old_record
        renewed_record = renewed_record[0] if isinstance(renewed_record, list) and renewed_record else renewed_record
        old_policy_record = get_policy_analysis_by_analysis_id(str((old_record or {}).get("policy_id") or ""))
        renewed_policy_record = get_policy_analysis_by_analysis_id(str((renewed_record or {}).get("policy_id") or ""))
        if not old_policy_record or not renewed_policy_record:
            return jsonify({"error": "Comparison service is unavailable and stored policy analysis was not found."}), 502
        comparison = {"output": build_local_policy_comparison(old_policy_record.get("extracted_data") or {}, renewed_policy_record.get("extracted_data") or {})}

    try:
        normalized_comparison = normalize_policy_comparison_response(comparison)
    except PolicyComparisonValidationError as exc:
        app.logger.error("Policy comparison response validation failed: %s", exc)
        return jsonify({"error": "Policy comparison returned an invalid result."}), 502

    comparison_id = uuid.uuid4().hex
    comparison_pdf = build_comparison_pdf(normalized_comparison, old_filename, renewed_filename)
    try:
        saved_record = create_policy_comparison(
            {
                "user_id": str(user.get("id")),
                "old_file_name": old_filename,
                "renewed_file_name": renewed_filename,
                "comparison_id": comparison_id,
                "comparison": normalized_comparison,
                "pdf_data": base64.b64encode(comparison_pdf).decode("ascii"),
                "pdf_filename": f"insura-comparison-{comparison_id}.pdf",
            }
        )
    except RuntimeError:
        app.logger.exception("Could not save policy comparison")
        return jsonify({"error": "Policy comparison could not be saved."}), 500

    return jsonify({"success": True, "comparison_id": comparison_id, "comparison": normalized_comparison, "id": str(saved_record.get("id")) if isinstance(saved_record, dict) and saved_record.get("id") is not None else None})


@app.route("/api/policy-comparisons/<comparison_id>/pdf", methods=["GET", "OPTIONS"])
@login_required
def comparison_pdf(comparison_id):
    if request.method == "OPTIONS": return "", 200
    user_id = str(get_current_user().get("id"))
    record = next((item for item in user_table_records("policy_comparison", user_id) if str(item.get("id")) == str(comparison_id) or str(item.get("comparison_id")) == str(comparison_id)), None)
    if not record: return jsonify({"error": "Comparison not found."}), 404
    if record.get("pdf_data"):
        pdf_bytes = base64.b64decode(record["pdf_data"])
    else:
        pdf_bytes = build_comparison_pdf(record.get("comparison") or {}, record.get("old_file_name") or "Existing policy", record.get("renewed_file_name") or "Renewed policy")
        __import__("database").db.merge(record["id"], {"pdf_data": base64.b64encode(pdf_bytes).decode("ascii"), "pdf_filename": f"insura-comparison-{record.get('comparison_id') or record.get('id')}.pdf"})
    pdf = io.BytesIO(pdf_bytes)
    return send_file(pdf, mimetype="application/pdf", as_attachment=False, download_name=record.get("pdf_filename") or "insura-comparison.pdf")


@app.route("/api/learning/generate", methods=["POST", "OPTIONS"])
def generate_learning():
    if request.method == "OPTIONS":
        return "", 200

    user = get_current_user()
    if not user:
        return jsonify({"error": "Please sign in first."}), 401

    data = request.get_json(silent=True) or {}
    policy_id = str(data.get("policy_id") or "").strip()
    policy_intelligence = data.get("policy_intelligence")
    if not policy_id or not isinstance(policy_intelligence, dict):
        return jsonify({"error": "policy_id and policy_intelligence are required."}), 400

    try:
        policy_record = get_policy_analysis(policy_id)
    except RuntimeError:
        return jsonify({"error": "Policy analysis could not be loaded."}), 500
    if not policy_record or str(policy_record.get("user_id")) != str(user.get("id")):
        return jsonify({"error": "You are not authorized to generate learning for this policy."}), 403

    try:
        generated = n8n_service.run_learning_generation(
            {"policy_intelligence": policy_intelligence, "policy_id": policy_id}
        )
        learning = normalize_learning_generation_response(generated)
    except (N8NServiceError, ValueError, LearningGenerationValidationError) as exc:
        app.logger.error("Learning generation request failed: %s", type(exc).__name__)
        return jsonify({"error": "Learning generation is temporarily unavailable."}), 502

    learning_generation_id = uuid.uuid4().hex
    try:
        saved_record = create_learning_generation(
            {
                "user_id": str(user.get("id")),
                "policy_id": policy_id,
                "learning_generation_id": learning_generation_id,
                "learning": learning,
            }
        )
    except RuntimeError:
        app.logger.exception("Could not save learning generation")
        return jsonify({"error": "Learning generation could not be saved."}), 500

    return jsonify({"success": True, "learning_generation_id": str(saved_record.get("id")) if isinstance(saved_record, dict) else learning_generation_id, "learning": learning})


@app.route("/api/learning/<learning_generation_id>", methods=["GET", "OPTIONS"])
def get_learning(learning_generation_id):
    if request.method == "OPTIONS":
        return "", 200

    user = get_current_user()
    if not user:
        return jsonify({"error": "Please sign in first."}), 401

    try:
        record = get_learning_generation(learning_generation_id)
    except RuntimeError:
        return jsonify({"error": "Learning could not be loaded."}), 500
    if not record:
        return jsonify({"error": "Learning not found."}), 404
    if str(record.get("user_id")) != str(user.get("id")):
        return jsonify({"error": "You are not authorized to access this learning."}), 403

    return jsonify({"success": True, "learning_generation_id": record.get("learning_generation_id"), "learning": record.get("learning") or {}})


@app.route("/api/policies/<policy_id>", methods=["GET", "OPTIONS"])
def get_policy(policy_id):
    if request.method == "OPTIONS":
        return "", 200

    user = get_current_user()
    if not user:
        return jsonify({"error": "Please sign in first."}), 401

    try:
        record = get_policy_analysis(policy_id)
    except RuntimeError:
        app.logger.exception("Could not retrieve policy analysis")
        return jsonify({"error": "Policy analysis could not be loaded."}), 500

    if not record:
        return jsonify({"error": "Policy analysis not found."}), 404
    if str(record.get("user_id")) != str(user.get("id")):
        return jsonify({"error": "You are not authorized to access this policy."}), 403

    return jsonify(
        {
            "success": True,
            "policy_id": str(record.get("id")),
            "analysis_id": record.get("analysis_id"),
            "output": record.get("extracted_data") or {},
            "file_name": record.get("file_name"),
            "created_at": record.get("created_at"),
        }
    )


@app.route("/auth/google")
def auth_google():
    frontend_url = resolve_frontend_url(request)
    session["frontend_url"] = frontend_url

    if not os.getenv("GOOGLE_CLIENT_ID") or not os.getenv("GOOGLE_CLIENT_SECRET"):
        return redirect(f"{frontend_url}/?auth=error&message=Google+OAuth+is+not+configured")

    backend_url = resolve_backend_url(request)
    redirect_uri = f"{backend_url}/auth/google/callback"
    session["google_redirect_uri"] = redirect_uri
    return oauth.google.authorize_redirect(redirect_uri)


@app.route("/auth/google/callback")
def auth_google_callback():
    frontend_url = session.get("frontend_url") or resolve_frontend_url(request)

    try:
        token = oauth.google.authorize_access_token()
        if token is None:
            raise ValueError("Missing token")
    except Exception:
        return redirect(f"{frontend_url}/?auth=error&message=Google+login+failed")

    userinfo = oauth.google.userinfo()
    if not userinfo:
        return redirect(f"{frontend_url}/?auth=error&message=Google+profile+could+not+be+loaded")

    google_id = str(userinfo.get("sub") or "")
    email = str(userinfo.get("email") or "").strip().lower()
    name = str(userinfo.get("name") or "").strip() or email.split("@", 1)[0].title()

    if not google_id or not email:
        return redirect(f"{frontend_url}/?auth=error&message=Google+account+did+not+return+an+email")

    existing_google_user = find_user_by_google_id(google_id)
    if existing_google_user:
        login_user(existing_google_user)
        return redirect(f"{frontend_url}/?view=app")

    existing_email_user = find_user_by_email(email)
    if existing_email_user and existing_email_user.get("auth_provider") != "google":
        return redirect(f"{frontend_url}/?auth=error&message=This+email+already+belongs+to+a+local+account")

    if existing_email_user and existing_email_user.get("auth_provider") == "google":
        login_user(existing_email_user)
        return redirect(f"{frontend_url}/?view=app")

    user = create_user(
        {
            "name": name,
            "email": email,
            "password_hash": None,
            "auth_provider": "google",
            "google_id": google_id,
            "email_verified": bool(userinfo.get("email_verified")),
        }
    )
    login_user(user)
    return redirect(f"{frontend_url}/?view=app")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
