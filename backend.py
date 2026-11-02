import json
import mimetypes
import re
import sqlite3
import urllib.parse
import urllib.request
import urllib.error
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "placement_quest.db"


def database():
    connection = sqlite3.connect(DB_PATH, timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database():
    with database() as connection:
        connection.executescript((ROOT / "database.sql").read_text(encoding="utf-8"))


def verify_firebase_token(token, expected_project):
    query = urllib.parse.urlencode({"idToken": token})
    request = urllib.request.Request(
        "https://www.googleapis.com/robot/v1/metadata/x509/securetoken@system.gserviceaccount.com",
        method="GET",
    )
    certificates_url = "https://www.googleapis.com/robot/v1/metadata/x509/securetoken@system.gserviceaccount.com"
    if expected_project:
        with urllib.request.urlopen(
            "https://identitytoolkit.googleapis.com/v1/accounts:lookup?" + query,
            timeout=10,
        ) as response:
            payload = json.loads(response.read().decode("utf-8"))
        if payload.get("users"):
            return payload["users"][0]["localId"], payload["users"][0]
        return None
    return None


class PlacementQuestHandler(BaseHTTPRequestHandler):
    server_version = "PlacementQuest/1.0"

    def send_json(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def read_json(self):
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0:
            return {}
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def authenticated_user(self):
        authorization = self.headers.get("Authorization", "")
        if not authorization.startswith("Bearer "):
            return None
        token = authorization.split(" ", 1)[1].strip()
        try:
            with urllib.request.urlopen(
                "https://oauth2.googleapis.com/tokeninfo?id_token=" + urllib.parse.quote(token, safe=""),
                timeout=10,
            ) as response:
                claims = json.loads(response.read().decode("utf-8"))
            project_match = re.search(r"projectId\s*:\s*['\"]([^'\"]+)['\"]", (ROOT / "index.html").read_text(encoding="utf-8"))
            project_id = project_match.group(1) if project_match else ""
            if project_id.startswith("YOUR_") or claims.get("aud") == project_id:
                return {
                    "localId": claims["sub"],
                    "email": claims.get("email", ""),
                    "displayName": claims.get("name"),
                    "photoUrl": claims.get("picture"),
                }
            return None
        except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, KeyError):
            return None

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/me":
            user = self.authenticated_user()
            if not user:
                self.send_json(401, {"error": "Authentication required"})
                return
            self.send_json(200, self.get_account(user["localId"], user))
            return

        if parsed.path == "/api/progress":
            user = self.authenticated_user()
            if not user:
                self.send_json(401, {"error": "Authentication required"})
                return
            self.send_json(200, self.get_progress(user["localId"]))
            return

        relative = parsed.path.lstrip("/") or "index.html"
        if parsed.path == "/database.sql":
            self.send_json(404, {"error": "Database schema is not public"})
            return
        requested = (ROOT / relative).resolve()
        if ROOT not in requested.parents and requested != ROOT:
            self.send_json(403, {"error": "Forbidden"})
            return
        if not requested.is_file() or requested.suffix.lower() in {".db", ".py"}:
            self.send_json(404, {"error": "Not found"})
            return
        content = requested.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", mimetypes.guess_type(requested.name)[0] or "application/octet-stream")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/users":
            user = self.authenticated_user()
            if not user:
                self.send_json(401, {"error": "Authentication required"})
                return
            self.save_account(user)
            self.send_json(200, self.get_account(user["localId"], user))
            return
        self.send_json(404, {"error": "Not found"})

    def do_PUT(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/progress":
            user = self.authenticated_user()
            if not user:
                self.send_json(401, {"error": "Authentication required"})
                return
            body = self.read_json()
            uid = user["localId"]
            state_json = json.dumps(body.get("state", {}), separators=(",", ":"))
            with database() as connection:
                connection.execute(
                    """INSERT INTO progress (uid, xp, challenge_started_at, aptitude_started_at, theme, state_json)
                       VALUES (?, ?, ?, ?, ?, ?)
                       ON CONFLICT(uid) DO UPDATE SET
                         xp=excluded.xp,
                         challenge_started_at=excluded.challenge_started_at,
                         aptitude_started_at=excluded.aptitude_started_at,
                         theme=excluded.theme,
                         state_json=excluded.state_json,
                         updated_at=datetime('now')""",
                    (
                        uid,
                        max(0, int(body.get("xp", 0))),
                        body.get("challengeStartedAt"),
                        body.get("aptitudeStartedAt"),
                        body.get("theme"),
                        state_json,
                    ),
                )
            self.send_json(200, {"saved": True})
            return
        self.send_json(404, {"error": "Not found"})

    def save_account(self, user):
        with database() as connection:
            connection.execute(
                """INSERT INTO users (uid, email, display_name, photo_url)
                   VALUES (?, ?, ?, ?)
                   ON CONFLICT(uid) DO UPDATE SET
                     email=excluded.email,
                     display_name=excluded.display_name,
                     photo_url=excluded.photo_url,
                     updated_at=datetime('now')""",
                (
                    user["localId"],
                    user.get("email", ""),
                    user.get("displayName"),
                    user.get("photoUrl"),
                ),
            )
            connection.execute(
                "INSERT OR IGNORE INTO progress (uid, state_json) VALUES (?, '{}')",
                (user["localId"],),
            )

    def get_account(self, uid, firebase_user):
        with database() as connection:
            row = connection.execute(
                "SELECT uid, email, display_name, photo_url FROM users WHERE uid = ?",
                (uid,),
            ).fetchone()
        if row:
            return dict(row)
        return {
            "uid": uid,
            "email": firebase_user.get("email", ""),
            "display_name": firebase_user.get("displayName"),
            "photo_url": firebase_user.get("photoUrl"),
        }

    def get_progress(self, uid):
        with database() as connection:
            row = connection.execute(
                """SELECT xp, challenge_started_at, aptitude_started_at, theme, state_json
                   FROM progress WHERE uid = ?""",
                (uid,),
            ).fetchone()
        if not row:
            return {"xp": 0, "challengeStartedAt": None, "state": {}}
        return {
            "xp": row["xp"],
            "challengeStartedAt": row["challenge_started_at"],
            "aptitudeStartedAt": row["aptitude_started_at"],
            "theme": row["theme"],
            "state": json.loads(row["state_json"]),
        }

    def log_message(self, format, *args):
        print(f"{self.address_string()} - {format % args}")


if __name__ == "__main__":
    initialize_database()
    server = ThreadingHTTPServer(("127.0.0.1", 8000), PlacementQuestHandler)
    print("Placement Quest backend: http://127.0.0.1:8000")
    server.serve_forever()
