from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app)  # VERY IMPORTANT for GitHub Pages frontend

# ---------------- PATH CONFIG ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, "hireme.db")

# ---------------- DATABASE ----------------
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Init DB
with get_db() as conn:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS hire_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            budget TEXT NOT NULL,
            message TEXT NOT NULL,
            time DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()

# ---------------- API : HEALTH CHECK ----------------
@app.route("/")
def health():
    return {"status": "Backend running"}

# ---------------- API : SEND MESSAGE ----------------
@app.route("/send", methods=["POST"])
def send():
    try:
        data = request.get_json()

        name = data.get("name")
        email = data.get("email")
        budget = data.get("budget")
        message = data.get("message")

        if not all([name, email, budget, message]):
            return jsonify({"status": "error", "msg": "Invalid input"}), 400

        with get_db() as conn:
            conn.execute(
                "INSERT INTO hire_requests (name, email, budget, message) VALUES (?, ?, ?, ?)",
                (name, email, budget, message)
            )
            conn.commit()

        return jsonify({"status": "success", "msg": "Message sent successfully"})

    except Exception as e:
        print("SERVER ERROR:", e)
        return jsonify({"status": "error", "msg": "Server error"}), 500

# ---------------- ADMIN API ----------------
@app.route("/admin/messages")
def admin_messages():
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM hire_requests ORDER BY time DESC"
        ).fetchall()

    return jsonify([dict(row) for row in rows])

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run()
