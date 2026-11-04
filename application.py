"""
app.py - Flask Application for HemoMatch
Connects compatibility.py (blood group logic) with database.db (SQLite records)
and renders index.html (main webpage) and history.html (previous check records).
"""

import os
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for

# Import blood group logic from compatibility.py
from compatibility import check_blood_compatibility, BLOOD_COMPATIBILITY

app = Flask(__name__)

# Database file configuration (database.db)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")


# ==========================================================
# Database Helper Functions (database.db)
# ==========================================================

def get_db_connection():
    """Create and return an SQLite connection with dict-like row access."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Ensure the history table exists in database.db."""
    with get_db_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                donor TEXT NOT NULL,
                recipient TEXT NOT NULL,
                result TEXT NOT NULL,
                status TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)
        conn.commit()


def save_history(donor: str, recipient: str, result: str, status: str):
    """Store a compatibility check record in database.db."""
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with get_db_connection() as conn:
        conn.execute(
            """
            INSERT INTO history (donor, recipient, result, status, timestamp)
            VALUES (?, ?, ?, ?, ?)
            """,
            (donor, recipient, result, status, now_str)
        )
        conn.commit()


def get_history(limit: int = 100):
    """Fetch previous check records from database.db, newest first."""
    with get_db_connection() as conn:
        cursor = conn.execute(
            """
            SELECT id, donor, recipient, result, status, timestamp
            FROM history
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,)
        )
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def clear_history_db():
    """Delete all records from the history table in database.db."""
    with get_db_connection() as conn:
        conn.execute("DELETE FROM history")
        conn.commit()


# Initialize SQLite table on startup
init_db()


# ==========================================================
# Flask Routes
# ==========================================================

@app.route("/", methods=["GET", "POST"])
def home():
    """
    Main webpage route:
    - GET: renders index.html with recent history count.
    - POST: receives selected blood groups, calls compatibility logic,
            saves result to database.db, and returns result to index.html.
    """
    donor = ""
    recipient = ""
    result = None

    if request.method == "POST":
        # Handle JSON fetch requests
        if request.is_json:
            data = request.get_json() or {}
            donor = data.get("donorBlood") or data.get("donor")
            recipient = data.get("recipientBlood") or data.get("recipient")
            result = check_blood_compatibility(donor, recipient)

            # Save valid checks to database.db
            if result.get("donor") and result.get("recipient") and result["status"] in ("compatible", "incompatible"):
                res_label = "Compatible" if result["compatible"] else "Not Compatible"
                save_history(result["donor"], result["recipient"], res_label, result["status"])

            result["history"] = get_history()
            return jsonify(result)

        # Standard HTML Form POST
        donor = request.form.get("donorBlood") or request.form.get("donor")
        recipient = request.form.get("recipientBlood") or request.form.get("recipient")
        result = check_blood_compatibility(donor, recipient)

        if result.get("donor") and result.get("recipient") and result["status"] in ("compatible", "incompatible"):
            res_label = "Compatible" if result["compatible"] else "Not Compatible"
            save_history(result["donor"], result["recipient"], res_label, result["status"])

        history = get_history()
        return render_template(
            "index.html",
            donor=donor,
            recipient=recipient,
            result=result,
            history=history
        )

    # Initial GET request
    history = get_history()
    return render_template("index.html", donor=donor, recipient=recipient, result=result, history=history)


@app.route("/history", methods=["GET"])
def history_page():
    """
    Previous check records route:
    - Renders history.html with stored records from database.db.
    - Also serves JSON if requested via API or query parameter ?format=json.
    """
    records = get_history()
    if request.is_json or request.args.get("format") == "json" or "application/json" in request.headers.get("Accept", ""):
        return jsonify(records)
    return render_template("history.html", history=records)


@app.route("/check", methods=["POST"])
def check_api():
    """API endpoint to check compatibility and log into database.db."""
    data = request.get_json() if request.is_json else request.form
    donor = data.get("donorBlood") or data.get("donor")
    recipient = data.get("recipientBlood") or data.get("recipient")
    result = check_blood_compatibility(donor, recipient)

    if result.get("donor") and result.get("recipient") and result["status"] in ("compatible", "incompatible"):
        res_label = "Compatible" if result["compatible"] else "Not Compatible"
        save_history(result["donor"], result["recipient"], res_label, result["status"])

    result["history"] = get_history()
    return jsonify(result)


@app.route("/clear-history", methods=["POST"])
def clear_history_action():
    """Clear all records from database.db and redirect to history page."""
    clear_history_db()
    if request.is_json:
        return jsonify({"success": True, "history": []})
    # Redirect back to the referrer or /history
    return redirect(request.referrer or url_for("history_page"))


if __name__ == "__main__":
    print("Starting HemoMatch server on http://127.0.0.1:5000")
    app.run(debug=True, host="127.0.0.1", port=5000)
