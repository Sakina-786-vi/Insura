import os
import base64
import re
from datetime import datetime, timezone

from dotenv import load_dotenv
from surrealdb import Surreal

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

SURREALDB_URL = os.getenv("SURREALDB_URL", "ws://127.0.0.1:8000")
SURREALDB_NAMESPACE = os.getenv("SURREALDB_NAMESPACE", "insura")
SURREALDB_DATABASE = os.getenv("SURREALDB_DATABASE", "main")
SURREALDB_USERNAME = os.getenv("SURREALDB_USERNAME", "root")
SURREALDB_PASSWORD = os.getenv("SURREALDB_PASSWORD", "root")

db = Surreal(SURREALDB_URL)


def connect_db():
    try:
        db.signin({
            "username": SURREALDB_USERNAME,
            "password": SURREALDB_PASSWORD,
        })
        db.use(SURREALDB_NAMESPACE, SURREALDB_DATABASE)
        return db
    except Exception as exc:
        raise RuntimeError(
            "Could not connect to SurrealDB. Check that the server is running and the credentials are correct."
        ) from exc


def ensure_user_table():
    schema = """
    DEFINE TABLE user SCHEMAFULL;
    DEFINE FIELD name ON TABLE user TYPE string;
    DEFINE FIELD email ON TABLE user TYPE string;
    DEFINE FIELD password_hash ON TABLE user TYPE option<string>;
    DEFINE FIELD auth_provider ON TABLE user TYPE string;
    DEFINE FIELD google_id ON TABLE user TYPE option<string>;
    DEFINE FIELD email_verified ON TABLE user TYPE bool DEFAULT false;
    DEFINE FIELD created_at ON TABLE user TYPE datetime DEFAULT time::now();
    DEFINE FIELD updated_at ON TABLE user TYPE datetime DEFAULT time::now();
    DEFINE INDEX idx_user_email ON TABLE user COLUMNS email UNIQUE;
    """

    try:
        db.query(schema)
    except Exception:
        pass


def ensure_policy_analysis_table():
    schema = """
    DEFINE TABLE policy_analysis SCHEMAFULL;
    DEFINE FIELD user_id ON TABLE policy_analysis TYPE string;
    DEFINE FIELD file_name ON TABLE policy_analysis TYPE string;
    DEFINE FIELD analysis_id ON TABLE policy_analysis TYPE string;
    DEFINE FIELD OVERWRITE extracted_data ON TABLE policy_analysis TYPE any;
    DEFINE FIELD created_at ON TABLE policy_analysis TYPE datetime DEFAULT time::now();
    """

    try:
        db.query(schema)
    except Exception:
        pass


def ensure_learning_generation_table():
    schema = """
    DEFINE TABLE learning_generation SCHEMAFULL;
    DEFINE FIELD user_id ON TABLE learning_generation TYPE string;
    DEFINE FIELD policy_id ON TABLE learning_generation TYPE string;
    DEFINE FIELD learning_generation_id ON TABLE learning_generation TYPE string;
    DEFINE FIELD learning ON TABLE learning_generation TYPE any;
    DEFINE FIELD created_at ON TABLE learning_generation TYPE datetime DEFAULT time::now();
    """

    try:
        db.query(schema)
    except Exception:
        pass


def ensure_policy_comparison_table():
    schema = """
    DEFINE TABLE policy_comparison SCHEMAFULL;
    DEFINE FIELD user_id ON TABLE policy_comparison TYPE string;
    DEFINE FIELD old_file_name ON TABLE policy_comparison TYPE string;
    DEFINE FIELD renewed_file_name ON TABLE policy_comparison TYPE string;
    DEFINE FIELD comparison_id ON TABLE policy_comparison TYPE string;
    DEFINE FIELD comparison ON TABLE policy_comparison TYPE any;
    DEFINE FIELD created_at ON TABLE policy_comparison TYPE datetime DEFAULT time::now();
    """

    try:
        db.query(schema)
    except Exception:
        pass


def ensure_policy_document_table():
    schema = """
    DEFINE TABLE policy_document SCHEMAFULL;
    DEFINE FIELD user_id ON TABLE policy_document TYPE string;
    DEFINE FIELD file_name ON TABLE policy_document TYPE string;
    DEFINE FIELD document_hash ON TABLE policy_document TYPE string;
    DEFINE FIELD status ON TABLE policy_document TYPE string DEFAULT 'uploaded';
    DEFINE FIELD processing_status ON TABLE policy_document TYPE string DEFAULT 'queued';
    DEFINE FIELD policy_id ON TABLE policy_document TYPE option<string>;
    DEFINE FIELD created_at ON TABLE policy_document TYPE datetime DEFAULT time::now();
    DEFINE FIELD updated_at ON TABLE policy_document TYPE datetime DEFAULT time::now();
    DEFINE INDEX idx_policy_document_user_hash ON TABLE policy_document COLUMNS user_id, document_hash UNIQUE;
    """

    try:
        db.query(schema)
    except Exception:
        pass


def ensure_user_progress_table():
    schema = """
    DEFINE TABLE user_progress SCHEMAFULL;
    DEFINE FIELD user_id ON TABLE user_progress TYPE string;
    DEFINE FIELD xp ON TABLE user_progress TYPE number DEFAULT 0;
    DEFINE FIELD streak ON TABLE user_progress TYPE number DEFAULT 0;
    DEFINE FIELD readiness ON TABLE user_progress TYPE number DEFAULT 0;
    DEFINE FIELD completed_levels ON TABLE user_progress TYPE number DEFAULT 0;
    DEFINE FIELD badges ON TABLE user_progress TYPE array DEFAULT [];
    DEFINE FIELD last_activity_date ON TABLE user_progress TYPE option<datetime>;
    DEFINE FIELD created_at ON TABLE user_progress TYPE datetime DEFAULT time::now();
    DEFINE FIELD updated_at ON TABLE user_progress TYPE datetime DEFAULT time::now();
    DEFINE INDEX idx_user_progress_user ON TABLE user_progress COLUMNS user_id UNIQUE;
    """

    try:
        db.query(schema)
    except Exception:
        pass


def ensure_learning_completion_table():
    schema = """
    DEFINE TABLE learning_completion SCHEMAFULL;
    DEFINE FIELD user_id ON TABLE learning_completion TYPE string;
    DEFINE FIELD policy_id ON TABLE learning_completion TYPE option<string>;
    DEFINE FIELD learning_id ON TABLE learning_completion TYPE string;
    DEFINE FIELD completion_key ON TABLE learning_completion TYPE string;
    DEFINE FIELD xp_awarded ON TABLE learning_completion TYPE number DEFAULT 0;
    DEFINE FIELD completed_at ON TABLE learning_completion TYPE datetime DEFAULT time::now();
    DEFINE INDEX idx_learning_completion_user_level ON TABLE learning_completion COLUMNS user_id, completion_key UNIQUE;
    """

    try:
        db.query(schema)
    except Exception:
        pass


def ensure_xp_transaction_table():
    schema = """
    DEFINE TABLE xp_transaction SCHEMAFULL;
    DEFINE FIELD user_id ON TABLE xp_transaction TYPE string;
    DEFINE FIELD activity_type ON TABLE xp_transaction TYPE string;
    DEFINE FIELD activity_id ON TABLE xp_transaction TYPE string;
    DEFINE FIELD xp_amount ON TABLE xp_transaction TYPE number DEFAULT 0;
    DEFINE FIELD reason ON TABLE xp_transaction TYPE string;
    DEFINE FIELD created_at ON TABLE xp_transaction TYPE datetime DEFAULT time::now();
    DEFINE INDEX idx_xp_transaction_user_activity ON TABLE xp_transaction COLUMNS user_id, activity_type, activity_id UNIQUE;
    """

    try:
        db.query(schema)
    except Exception:
        pass


def ensure_badge_table():
    schema = """
    DEFINE TABLE badge SCHEMAFULL;
    DEFINE FIELD user_id ON TABLE badge TYPE string;
    DEFINE FIELD name ON TABLE badge TYPE string;
    DEFINE FIELD description ON TABLE badge TYPE string;
    DEFINE FIELD awarded_xp ON TABLE badge TYPE number DEFAULT 0;
    DEFINE FIELD unlocked_at ON TABLE badge TYPE datetime DEFAULT time::now();
    DEFINE INDEX idx_badge_user_name ON TABLE badge COLUMNS user_id, name UNIQUE;
    """

    try:
        db.query(schema)
    except Exception:
        pass


def ensure_simulation_completion_table():
    schema = """
    DEFINE TABLE simulation_completion SCHEMAFULL;
    DEFINE FIELD user_id ON TABLE simulation_completion TYPE string;
    DEFINE FIELD simulation_id ON TABLE simulation_completion TYPE string;
    DEFINE FIELD scenario_id ON TABLE simulation_completion TYPE string;
    DEFINE FIELD completed_steps ON TABLE simulation_completion TYPE number DEFAULT 0;
    DEFINE FIELD xp_awarded ON TABLE simulation_completion TYPE number DEFAULT 0;
    DEFINE FIELD readiness_gain ON TABLE simulation_completion TYPE number DEFAULT 0;
    DEFINE FIELD result ON TABLE simulation_completion TYPE any;
    DEFINE FIELD completed_at ON TABLE simulation_completion TYPE datetime DEFAULT time::now();
    DEFINE INDEX idx_simulation_completion_user_scenario ON TABLE simulation_completion COLUMNS user_id, scenario_id UNIQUE;
    """

    try:
        db.query(schema)
    except Exception:
        pass


def ensure_chat_tables():
    schema = """
    DEFINE TABLE chat SCHEMAFULL;
    DEFINE FIELD user_id ON TABLE chat TYPE string;
    DEFINE FIELD title ON TABLE chat TYPE string;
    DEFINE FIELD created_at ON TABLE chat TYPE datetime DEFAULT time::now();
    DEFINE FIELD updated_at ON TABLE chat TYPE datetime DEFAULT time::now();
    DEFINE TABLE chat_message SCHEMAFULL;
    DEFINE FIELD chat_id ON TABLE chat_message TYPE string;
    DEFINE FIELD user_id ON TABLE chat_message TYPE string;
    DEFINE FIELD role ON TABLE chat_message TYPE string;
    DEFINE FIELD content ON TABLE chat_message TYPE string;
    DEFINE FIELD created_at ON TABLE chat_message TYPE datetime DEFAULT time::now();
    DEFINE INDEX idx_chat_user_updated ON TABLE chat COLUMNS user_id, updated_at;
    DEFINE INDEX idx_chat_message_chat_created ON TABLE chat_message COLUMNS chat_id, created_at;
    """

    try:
        db.query(schema)
    except Exception:
        pass


def ensure_policy_share_table():
    schema = """
    DEFINE TABLE policy_share SCHEMAFULL;
    DEFINE FIELD user_id ON TABLE policy_share TYPE string;
    DEFINE FIELD policy_id ON TABLE policy_share TYPE string;
    DEFINE FIELD share_token ON TABLE policy_share TYPE string;
    DEFINE FIELD created_at ON TABLE policy_share TYPE datetime DEFAULT time::now();
    DEFINE FIELD active ON TABLE policy_share TYPE bool DEFAULT true;
    DEFINE FIELD expires_at ON TABLE policy_share TYPE option<datetime>;
    DEFINE INDEX idx_policy_share_token ON TABLE policy_share COLUMNS share_token UNIQUE;
    DEFINE INDEX idx_policy_share_user_policy ON TABLE policy_share COLUMNS user_id, policy_id UNIQUE;
    """

    try:
        db.query(schema)
    except Exception:
        pass


def ensure_feature_tables():
    schema = """
    DEFINE FIELD storage_path ON TABLE policy_document TYPE option<string>;
    DEFINE FIELD file_data ON TABLE policy_document TYPE option<string>;
    DEFINE FIELD mime_type ON TABLE policy_document TYPE option<string>;
    DEFINE FIELD pdf_data ON TABLE policy_comparison TYPE option<string>;
    DEFINE FIELD pdf_filename ON TABLE policy_comparison TYPE option<string>;
    DEFINE TABLE reminder SCHEMAFULL;
    DEFINE FIELD user_id ON TABLE reminder TYPE string;
    DEFINE FIELD title ON TABLE reminder TYPE string;
    DEFINE FIELD reminder_type ON TABLE reminder TYPE string;
    DEFINE FIELD due_at ON TABLE reminder TYPE datetime;
    DEFINE FIELD status ON TABLE reminder TYPE string DEFAULT 'open';
    DEFINE FIELD notes ON TABLE reminder TYPE option<string>;
    DEFINE FIELD created_at ON TABLE reminder TYPE datetime DEFAULT time::now();
    DEFINE FIELD updated_at ON TABLE reminder TYPE datetime DEFAULT time::now();
    DEFINE TABLE support_ticket SCHEMAFULL;
    DEFINE FIELD user_id ON TABLE support_ticket TYPE string;
    DEFINE FIELD subject ON TABLE support_ticket TYPE string;
    DEFINE FIELD message ON TABLE support_ticket TYPE string;
    DEFINE FIELD status ON TABLE support_ticket TYPE string DEFAULT 'open';
    DEFINE FIELD created_at ON TABLE support_ticket TYPE datetime DEFAULT time::now();
    DEFINE TABLE claim SCHEMAFULL;
    DEFINE FIELD user_id ON TABLE claim TYPE string;
    DEFINE FIELD policy_id ON TABLE claim TYPE string;
    DEFINE FIELD details ON TABLE claim TYPE string;
    DEFINE FIELD status ON TABLE claim TYPE string DEFAULT 'draft';
    DEFINE FIELD created_at ON TABLE claim TYPE datetime DEFAULT time::now();
    DEFINE FIELD updated_at ON TABLE claim TYPE datetime DEFAULT time::now();
    DEFINE TABLE user_setting SCHEMAFULL;
    DEFINE FIELD user_id ON TABLE user_setting TYPE string;
    DEFINE FIELD settings ON TABLE user_setting TYPE any;
    DEFINE FIELD updated_at ON TABLE user_setting TYPE datetime DEFAULT time::now();
    """
    try:
        db.query(schema)
    except Exception:
        pass


connect_db()
ensure_user_table()
ensure_policy_analysis_table()
ensure_learning_generation_table()
ensure_policy_comparison_table()
ensure_policy_document_table()
ensure_user_progress_table()
ensure_learning_completion_table()
ensure_xp_transaction_table()
ensure_badge_table()
ensure_simulation_completion_table()
ensure_chat_tables()
ensure_policy_share_table()
ensure_feature_tables()


def get_db():
    return db


def create_policy_share(share_data):
    try:
        return db.create("policy_share", share_data)
    except Exception as exc:
        raise RuntimeError("Could not create the policy share in SurrealDB.") from exc


def get_policy_share_for_user(user_id, policy_id):
    if not user_id or not policy_id:
        return None
    for share in db.select("policy_share") or []:
        if str(share.get("user_id", "")) == str(user_id) and str(share.get("policy_id", "")) == str(policy_id) and share.get("active") is not False:
            return share
    return None


def get_policy_share_by_token(share_token):
    if not share_token:
        return None
    for share in db.select("policy_share") or []:
        if str(share.get("share_token", "")) == str(share_token) and share.get("active") is not False:
            return share
    return None


def create_chat(chat_data):
    try:
        return db.create("chat", chat_data)
    except Exception as exc:
        raise RuntimeError("Could not create the chat in SurrealDB.") from exc


def update_chat(chat_id, chat_data):
    try:
        return db.merge(str(chat_id), chat_data)
    except Exception as exc:
        raise RuntimeError("Could not update the chat in SurrealDB.") from exc


def create_chat_message(message_data):
    try:
        return db.create("chat_message", message_data)
    except Exception as exc:
        raise RuntimeError("Could not store the chat message in SurrealDB.") from exc


def get_chats_for_user(user_id):
    if not user_id:
        return []
    chats = [chat for chat in db.select("chat") or [] if str(chat.get("user_id", "")) == str(user_id)]
    return sorted(chats, key=lambda chat: str(chat.get("updated_at") or chat.get("created_at") or ""), reverse=True)


def get_chat_for_user(user_id, chat_id):
    if not user_id or not chat_id:
        return None
    for chat in get_chats_for_user(user_id):
        if str(chat.get("id", "")) == str(chat_id):
            return chat
    return None


def get_chat_messages(chat_id, user_id):
    if not chat_id or not user_id:
        return []
    messages = [
        message for message in db.select("chat_message") or []
        if str(message.get("chat_id", "")) == str(chat_id)
        and str(message.get("user_id", "")) == str(user_id)
    ]
    return sorted(messages, key=lambda message: str(message.get("created_at") or ""))


def get_all_users():
    try:
        return db.select("user") or []
    except Exception:
        return []


def find_user_by_email(email):
    normalized_email = (email or "").strip().lower()
    if not normalized_email:
        return None

    for user in get_all_users():
        if str(user.get("email", "")).lower() == normalized_email:
            return user
    return None


def find_user_by_google_id(google_id):
    normalized_google_id = (google_id or "").strip()
    if not normalized_google_id:
        return None

    for user in get_all_users():
        if str(user.get("google_id", "")) == normalized_google_id:
            return user
    return None


def find_user_by_id(user_id):
    if not user_id:
        return None
    try:
        record = db.select(str(user_id))
        if isinstance(record, list):
            return record[0] if record else None
        return record
    except Exception:
        return None


def create_user(user_data):
    try:
        return db.create("user", user_data)
    except Exception as exc:
        raise RuntimeError("Could not create the user account in SurrealDB.") from exc


def update_user(user_id, user_data):
    try:
        return db.update(str(user_id), user_data)
    except Exception as exc:
        raise RuntimeError("Could not update the user account in SurrealDB.") from exc


def create_policy_analysis(analysis_data):
    try:
        return db.create("policy_analysis", analysis_data)
    except Exception as exc:
        raise RuntimeError("Could not store the policy analysis in SurrealDB.") from exc


def get_policy_analysis(analysis_id):
    try:
        record = db.select(str(analysis_id))
        if isinstance(record, list):
            return record[0] if record else None
        return record
    except Exception as exc:
        raise RuntimeError("Could not retrieve the policy analysis from SurrealDB.") from exc


def create_learning_generation(generation_data):
    try:
        return db.create("learning_generation", generation_data)
    except Exception as exc:
        raise RuntimeError("Could not store the learning generation in SurrealDB.") from exc


def get_learning_generation(generation_id):
    try:
        record = db.select(str(generation_id))
        if isinstance(record, list):
            return record[0] if record else None
        return record
    except Exception as exc:
        raise RuntimeError("Could not retrieve the learning generation from SurrealDB.") from exc


def create_policy_comparison(comparison_data):
    try:
        return db.create("policy_comparison", comparison_data)
    except Exception as exc:
        raise RuntimeError("Could not store the policy comparison in SurrealDB.") from exc


def create_policy_document(document_data):
    try:
        return db.create("policy_document", document_data)
    except Exception as exc:
        raise RuntimeError("Could not store the uploaded policy document in SurrealDB.") from exc


def find_policy_document_by_hash(user_id, document_hash):
    if not user_id or not document_hash:
        return None

    for document in db.select("policy_document") or []:
        if str(document.get("user_id", "")) == str(user_id) and str(document.get("document_hash", "")) == str(document_hash):
            return document
    return None


def get_policy_documents_for_user(user_id):
    if not user_id:
        return []
    return [
        item for item in db.select("policy_document") or []
        if str(item.get("user_id", "")) == str(user_id)
        and str(item.get("status", "")) != "deleted"
    ]


def get_policy_document_for_user(user_id, document_id):
    if not user_id or not document_id:
        return None
    normalized_id = str(document_id)
    return next((item for item in get_policy_documents_for_user(user_id) if str(item.get("id")) == normalized_id), None)


def read_policy_document_bytes(user_id, document_id):
    document = get_policy_document_for_user(user_id, document_id)
    if not document:
        raise FileNotFoundError("Document does not belong to the authenticated user")

    storage_path = document.get("storage_path")
    if storage_path and os.path.isfile(storage_path):
        with open(storage_path, "rb") as stored_file:
            return document, stored_file.read()

    encoded_data = document.get("file_data")
    if not encoded_data:
        raise FileNotFoundError(f"Original binary is unavailable for {document_id}")

    try:
        file_bytes = base64.b64decode(encoded_data, validate=True)
    except (ValueError, TypeError, base64.binascii.Error) as exc:
        raise ValueError(f"Stored document data is corrupt for {document_id}") from exc

    safe_user = re.sub(r"[^A-Za-z0-9_.-]+", "_", str(user_id)).strip("._") or "user"
    safe_document = re.sub(r"[^A-Za-z0-9_.-]+", "_", str(document.get("id"))).strip("._") or "document"
    safe_name = re.sub(r"[^A-Za-z0-9_.-]+", "_", str(document.get("file_name") or "policy.pdf")).strip("._") or "policy.pdf"
    storage_dir = os.path.join(BASE_DIR, "uploads", "documents", safe_user)
    os.makedirs(storage_dir, exist_ok=True)
    restored_path = os.path.join(storage_dir, f"{safe_document}_{safe_name}")
    with open(restored_path, "wb") as restored_file:
        restored_file.write(file_bytes)
    db.merge(document["id"], {"storage_path": restored_path, "mime_type": "application/pdf"})
    document["storage_path"] = restored_path
    return document, file_bytes


def get_policy_status_for_user(user_id):
    documents = get_policy_documents_for_user(user_id)
    if not documents:
        return {"has_document": False, "document_count": 0, "status": None, "document_id": None}

    priority = {"processed": 3, "processing": 2, "uploaded": 1, "failed": 0}
    document = max(documents, key=lambda item: priority.get(str(item.get("processing_status") or item.get("status") or ""), 0))
    return {
        "has_document": True,
        "document_count": len(documents),
        "status": str(document.get("processing_status") or document.get("status") or "uploaded"),
        "document_id": str(document.get("id")) if document.get("id") else None,
        "policy_id": str(document.get("policy_id")) if document.get("policy_id") else None,
    }


def create_or_update_user_progress(user_id, progress_data):
    if not user_id:
        return None

    existing = get_user_progress(str(user_id))
    payload = dict(progress_data)
    payload["user_id"] = str(user_id)
    now = to_surreal_datetime()
    payload["created_at"] = to_surreal_datetime(existing.get("created_at")) if existing else now
    payload["updated_at"] = now

    if existing and existing.get("id"):
        return db.update(str(existing["id"]), payload)
    return db.create("user_progress", payload)


def to_surreal_datetime(value=None):
    if value is None:
        return datetime.now(timezone.utc)

    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    if isinstance(value, str):
        text = value.strip()
        if not text:
            return datetime.now(timezone.utc)
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        try:
            parsed = datetime.fromisoformat(text)
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            return parsed.astimezone(timezone.utc)
        except ValueError:
            pass

    return datetime.now(timezone.utc)


def get_user_progress(user_id):
    if not user_id:
        return None

    for progress in db.select("user_progress") or []:
        if str(progress.get("user_id", "")) == str(user_id):
            return progress
    return None


def has_user_policy(user_id):
    if not user_id:
        return False

    user_key = str(user_id)
    for record in db.select("policy_analysis") or []:
        if str(record.get("user_id", "")) == user_key:
            return True

    for record in db.select("policy_document") or []:
        if str(record.get("user_id", "")) == user_key and str(record.get("processing_status", "")) == "done":
            return True

    return False


def get_policy_analysis_by_analysis_id(analysis_id):
    if not analysis_id:
        return None

    for record in db.select("policy_analysis") or []:
        if str(record.get("analysis_id", "")) == str(analysis_id):
            return record
    return None


def get_policy_analysis_by_record_id(record_id):
    if not record_id:
        return None

    try:
        record = db.select(str(record_id))
        if isinstance(record, list):
            return record[0] if record else None
        return record
    except Exception:
        return None


def create_learning_completion(completion_data):
    try:
        return db.create("learning_completion", completion_data)
    except Exception as exc:
        raise RuntimeError("Could not record the learning completion in SurrealDB.") from exc


def create_xp_transaction(transaction_data):
    try:
        return db.create("xp_transaction", transaction_data)
    except Exception as exc:
        raise RuntimeError("Could not record the XP transaction in SurrealDB.") from exc


def find_xp_transaction(user_id, activity_type, activity_id):
    if not user_id or not activity_type or not activity_id:
        return None

    for transaction in db.select("xp_transaction") or []:
        if str(transaction.get("user_id", "")) == str(user_id) and str(transaction.get("activity_type", "")) == str(activity_type) and str(transaction.get("activity_id", "")) == str(activity_id):
            return transaction
    return None


def create_badge(badge_data):
    try:
        return db.create("badge", badge_data)
    except Exception as exc:
        raise RuntimeError("Could not record the badge in SurrealDB.") from exc


def get_badges_for_user(user_id):
    if not user_id:
        return []

    return [badge for badge in db.select("badge") or [] if str(badge.get("user_id", "")) == str(user_id)]


def create_simulation_completion(completion_data):
    try:
        return db.create("simulation_completion", completion_data)
    except Exception as exc:
        raise RuntimeError("Could not record the simulation completion in SurrealDB.") from exc


def find_simulation_completion(user_id, scenario_id):
    if not user_id or not scenario_id:
        return None

    for completion in db.select("simulation_completion") or []:
        if str(completion.get("user_id", "")) == str(user_id) and str(completion.get("scenario_id", "")) == str(scenario_id):
            return completion
    return None


def get_simulation_completions_for_user(user_id):
    if not user_id:
        return []
    return [item for item in db.select("simulation_completion") or [] if str(item.get("user_id", "")) == str(user_id)]


def find_learning_completion(user_id, completion_key):
    if not user_id or not completion_key:
        return None

    for completion in db.select("learning_completion") or []:
        if str(completion.get("user_id", "")) == str(user_id) and str(completion.get("completion_key", "")) == str(completion_key):
            return completion
    return None
