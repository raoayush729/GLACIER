import logging
from fastapi import FastAPI, Query
from pydantic import BaseModel
from agents.brain import Brain
from fastapi.encoders import jsonable_encoder
import pandas as pd
from collections import deque
from threading import Lock

import os
from dotenv import load_dotenv

# Load environment variables from .env file when the API server starts
load_dotenv()

app = FastAPI(title="GLACIER API")


class QuietPolling(logging.Filter):
    """Hide the constant voice polling lines from the uvicorn access log."""

    def filter(self, record):
        message = record.getMessage()
        return "/voice-state" not in message and "/voice-event/next" not in message


logging.getLogger("uvicorn.access").addFilter(QuietPolling())

# Shared voice state: stable / listening / executing / responding.
voice_state = {"mode": "stable", "partial": ""}
voice_commands = deque()
voice_lock = Lock()
VOICE_MODES = {"stable", "listening", "executing", "responding"}


class VoiceEvent(BaseModel):
    type: str
    message: str = ""
    status: str = ""
    mode: str = ""


@app.post("/voice-event")
def receive_voice_event(event: VoiceEvent):
    with voice_lock:
        if event.type == "mode" and event.mode in VOICE_MODES:
            voice_state["mode"] = event.mode
            voice_state["partial"] = ""
        elif event.type == "partial":
            voice_state["partial"] = event.message
        elif event.type == "command" and event.message.strip():
            voice_commands.append(event.message.strip())
            voice_state["mode"] = "executing"
            voice_state["partial"] = ""
        elif event.type != "status":
            return {"success": False, "error": "Invalid event"}
    return {"success": True}


@app.get("/voice-state")
def get_voice_state():
    with voice_lock:
        return dict(voice_state)


@app.get("/voice-event/next")
def get_next_voice_event():
    with voice_lock:
        state = dict(voice_state)
        if voice_commands:
            return {"type": "command", "message": voice_commands.popleft(), **state}
        return {"type": "none", **state}


# Create one persistent instance of GLACIER's existing brain.
brain = Brain()


class ChatRequest(BaseModel):   # This defines the format of incoming chat requests. It expects a message field containing text.
    message: str
    voice: bool = False   # True when the request came from the voice assistant


class SQLCredentialsRequest(BaseModel):
    username: str
    host: str
    password: str
    port: int | None = None


class SQLConnectionTestRequest(BaseModel):
    username: str
    host: str
    password: str
    port: int | None = None


@app.get("/health")
def health_check():          # This is a standalone function registered as the handler for GET /health.
    return {
        "status": "online",
        "application": "GLACIER"
    }

def make_spoken_summary(question, answer):
    """Turn a detailed chat reply into 1-2 short sentences that sound natural out loud."""
    plain = " ".join(answer.replace("*", " ").replace("`", " ").replace("#", " ").split())

    # Already short and simple: speak it as it is.
    if len(answer) <= 220 and "\n" not in answer.strip():
        return plain

    prompt = f"""You are GLACIER, speaking out loud to Ayush, your user.

USER REQUEST:
{question}

FULL WRITTEN REPLY (shown on screen):
{answer[:3000]}

Write what you would SAY out loud about this reply:
- 1 or 2 short, natural sentences (about 35 words at most).
- Give only the most important finding or result.
- No lists, markdown, symbols, or long number sequences; round numbers when natural.
- If the reply contains many details, end by saying the details are in the chat.
- Never invent facts that are not in the reply.
Return ONLY the spoken text."""

    try:
        spoken = brain.ask_qwen_stream_offf(prompt, num_predict=100).strip()
        if spoken:
            return spoken
    except Exception as error:
        print("Spoken summary failed:", type(error).__name__)

    # Fallback: first sentence plus a pointer to the chat.
    first = plain.split(". ")[0][:200]
    return first + ". The details are in the chat."


@app.post("/chat")
def chat(request: ChatRequest):        # This is another standalone function, registered as the handler for POST /chat. It receives a request validated against the ChatRequest model.
    message = request.message.strip()

    if not message:
        return {
            "success": False,
            "response": "Please enter a message.",
            "action_output": None,
            "dataset_viewer": None

        }

    # Clear any previous SQL results before processing this request.
    brain.action_output = None


    brain.dataset_viewer_output = None

    try:
        response = brain.Master_Mind(message)

        # Retrieve SQL results generated during this request.
        action_output = brain.action_output

        dataset_viewer = brain.dataset_viewer_output

        return {
                "success": True,
                "response": str(response),
                "spoken": make_spoken_summary(message, str(response)) if request.voice else None,
                "action_output": jsonable_encoder(action_output),
                "dataset_viewer": jsonable_encoder(dataset_viewer)
            }

    except Exception as error:
        print(f"GLACIER API error: {error}")

        return {
            "success": False,
            "response": (
                "GLACIER encountered an error while processing your request."
            ),
            "action_output": jsonable_encoder(brain.action_output),
            "dataset_viewer": jsonable_encoder(
                brain.dataset_viewer_output
            )
        }

@app.get("/dataset/rows")
def get_dataset_rows(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=200)
):
    # Get the currently active DataFrame.
    df = brain.dataset_manager.dataframe

    if df is None:
        return {
            "success": False,
            "message": "No active dataset is loaded."
        }

    # Select only the requested page of rows.
    page = df.iloc[offset:offset + limit]

    # Prepare rows for JSON output.
    rows = []

    for row in page.itertuples(index=False, name=None):
        safe_row = []

        for value in row:
            if pd.isna(value):
                safe_row.append(None)
            elif hasattr(value, "item"):
                safe_row.append(value.item())
            elif hasattr(value, "isoformat"):
                safe_row.append(value.isoformat())
            else:
                safe_row.append(value)

        rows.append(safe_row)

    # Return the selected rows and pagination information.
    return {
        "success": True,
        "columns": [str(column) for column in df.columns],
        "rows": jsonable_encoder(rows),
        "offset": offset,
        "limit": limit,
        "total_rows": len(df)
    }



@app.post("/sql-access/test")
def test_sql_connection(request: SQLConnectionTestRequest):
    connection = None

    try:
        export_manager = brain.export_manager

        connection_settings = {
            "Host": request.host.strip(),
            "User": request.username.strip(),
            "Password": request.password
        }

        if request.port is not None:
            connection_settings["Port"] = request.port

        connection = export_manager.connect_to_mysql(
            **connection_settings,
            Database=None
        )

        return {
            "success": True,
            "message": "MySQL connection successful."
        }

    except Exception as error:
        # Log only the exception type, never the credentials.
        print("MySQL connection test failed:", type(error).__name__)

        return {
            "success": False,
            "error": "MYSQL_CONNECTION_FAILED",
            "message": (
                "Could not connect to MySQL. Check the host, port, "
                "username, password, and server status."
            )
        }

    finally:
        if connection is not None:
            try:
                connection.close()
            except Exception:
                pass


@app.get("/sql-access/status")
def sql_access_status():
    credentials = brain.sql_credentials

    return {
        "success": True,
        "connected": bool(
            credentials.get("Host")
            and credentials.get("User")
            and credentials.get("Password")
        ),
        "host": credentials.get("Host"),
        "username": credentials.get("User"),
        "port": credentials.get("Port"),
        "password_configured": bool(
            credentials.get("Password")
        )
    }


@app.post("/sql-access/disconnect")
def disconnect_sql_access():
    try:
        brain.sql_credentials = {
            "Host": None,
            "User": None,
            "Password": None,
            "Port": None
        }

        return {
            "success": True,
            "message": "MySQL credentials cleared."
        }

    except Exception as error:
        print("SQL disconnect failed:", type(error).__name__)

        return {
            "success": False,
            "error": "SQL_DISCONNECT_FAILED",
            "message": "Could not clear the saved MySQL credentials."
        }


@app.post("/sql-access")
def save_sql_credentials(request: SQLCredentialsRequest):
    try:
        result = brain.update_sql_credentials(
            username=request.username,
            host=request.host,
            port=request.port,
            password=request.password
        )

        return result

    except Exception as error:
        print("SQL ACCESS update failed:", type(error).__name__)

        return {
            "success": False,
            "error": "SQL_CREDENTIALS_UPDATE_FAILED",
            "message": "Could not update MySQL connection settings."
        }



# ======================= STOP BUTTON SUPPORT =======================
import threading

_run_state = threading.local()      # remembers which request the current thread belongs to
_active_runs = []                   # requests that are running right now
_runs_lock = threading.Lock()


class _Run:
    def __init__(self):
        self.cancelled = threading.Event()   # set by /cancel
        self.done = threading.Event()        # set when Master_Mind finishes
        self.result = None
        self.error = None


_original_master_mind = brain.Master_Mind


def _stoppable_master_mind(prompt, *args, **kwargs):
    run = _Run()
    with _runs_lock:
        _active_runs.append(run)

    def worker():
        _run_state.run = run
        try:
            run.result = _original_master_mind(prompt, *args, **kwargs)
        except Exception as error:
            run.error = error
        finally:
            run.done.set()

    threading.Thread(target=worker, daemon=True).start()

    # Wait for either "finished" or "user pressed Stop".
    while not run.done.is_set() and not run.cancelled.is_set():
        run.done.wait(0.1)

    with _runs_lock:
        if run in _active_runs:
            _active_runs.remove(run)

    if not run.done.is_set():
        return "Stopped by user."
    if run.error:
        raise run.error
    return run.result


brain.Master_Mind = _stoppable_master_mind


# Once a request is stopped, its remaining steps must not run.
def _skip_when_stopped(method_name, fallback):
    original = getattr(brain, method_name, None)
    if original is None:
        return

    def wrapper(*args, **kwargs):
        run = getattr(_run_state, "run", None)
        if run is not None and run.cancelled.is_set():
            return fallback
        return original(*args, **kwargs)

    setattr(brain, method_name, wrapper)


_skip_when_stopped("retrieve_method_knowledge", None)
_skip_when_stopped("select_method_and_arguments", None)
_skip_when_stopped("execute_tool", {"success": False, "result": "Stopped by user. This step was not executed."})
_skip_when_stopped("ask_qwen_stream_offf", "Stopped by user.")
_skip_when_stopped("handle_tool_result", "Stopped by user.")


@app.post("/cancel")
def cancel_request():
    with _runs_lock:
        runs = list(_active_runs)

    for run in runs:
        run.cancelled.set()

    # If a Yes / No / Edit card is open, answer it with "No" so nothing waits forever.
    if hasattr(brain, "approval_event"):
        with brain.approval_lock:
            if brain.pending_approval is not None and brain.approval_response is None:
                brain.approval_response = {"decision": "no", "reason": "Stopped by user.", "edits": {}}
                brain.approval_event.set()

    return {"ok": True, "cancelled": len(runs)}




@app.post("/dataset/reload")
def reload_dataset_viewer():
    # Run show_active_dataset() again; it publishes fresh info to brain.dataset_viewer_output.
    result = brain.dataset_manager.show_active_dataset()

    if not result.get("success"):
        return {
            "success": False,
            "message": result.get("message", "Could not reload the dataset.")
        }

    return {
        "success": True,
        "message": result.get("message"),
        "dataset_viewer": jsonable_encoder(brain.dataset_viewer_output)
    }
# ===================================================================