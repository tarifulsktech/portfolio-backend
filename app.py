
from flask import Flask, request, jsonify, send_from_directory
import sqlite3
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "..", "frontend")
DB_PATH = os.path.join(BASE_DIR, "hireme.db")

# ---------- DATABASE ----------
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Init DB
conn = get_db()
conn.execute("""
CREATE TABLE IF NOT EXISTS hire_requests(
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 name TEXT NOT NULL,
 email TEXT NOT NULL,
 budget TEXT NOT NULL,
 message TEXT NOT NULL,
 time DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()
conn.close()

# ---------- API : SEND MESSAGE ----------
@app.route("/send", methods=["POST"])
def send():
    try:
        data = request.get_json(force=True)

        name = data.get("name")
        email = data.get("email")
        budget = data.get("budget")
        message = data.get("message")

        # Validation
        if not all([name, email, budget, message]):
            return jsonify({
                "status": "error",
                "msg": "Invalid input"
            }), 400

        conn = get_db()
        conn.execute(
            "INSERT INTO hire_requests(name,email,budget,message) VALUES(?,?,?,?)",
            (name, email, budget, message)
        )
        conn.commit()
        conn.close()

        return jsonify({
            "status": "success",
            "msg": "Message saved successfully"
        })

    except Exception as e:
        print("SERVER ERROR:", e)
        return jsonify({
            "status": "error",
            "msg": "Server error"
        }), 500


# ---------- OPTIONAL: ADMIN API (future use) ----------
@app.route("/admin/messages")
def admin_messages():
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM hire_requests ORDER BY time DESC"
    ).fetchall()
    conn.close()

    data = [dict(row) for row in rows]
    return jsonify(data)


# ---------- FRONTEND ----------
@app.route("/")
def home():
    return send_from_directory(FRONTEND_DIR, "index.html")

@app.route("/<path:path>")
def static_files(path):
    return send_from_directory(FRONTEND_DIR, path)

# ---------- RUN ----------
if __name__ == "__main__":
    app.run(debug=True)
