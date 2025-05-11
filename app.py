from flask import Flask, render_template, request, redirect, url_for, session
import os, random
from datetime import datetime
import sqlite3
import uuid

app = Flask(__name__)
app.secret_key = "your_secret_key"

IMAGE_FOLDER = "static/images"
ALL_IMAGES = os.listdir(IMAGE_FOLDER)
TOTAL_IMAGES = len(ALL_IMAGES)


def init_db():
    conn = sqlite3.connect("responses.db")
    c = conn.cursor()
    c.execute("""
    CREATE TABLE responses (
    id INTEGER PRIMARY KEY,     <-- ✅ This is the 6th column
    user_id TEXT,
    timestamp TEXT,
    age INTEGER,
    image TEXT,
    arousal INTEGER,
    valence INTEGER
)
    """)
    conn.commit()
    conn.close()


try:
    init_db()
except sqlite3.OperationalError as e:
    print("Database already exists. Skipping init.")

@app.route("/start", methods=["GET", "POST"])
def start():
    if request.method == "POST":
        age = request.form.get("age")
        if age and age.isdigit():
            session["age"] = int(age)
            session["seen"] = []
            session["user_id"] = str(uuid.uuid4())
            return redirect(url_for("index"))
        else:
            return render_template("start.html", error="Please enter a valid age")
    return render_template("start.html")

@app.route("/", methods=["GET", "POST"])
def index():
    if "seen" not in session or "age" not in session:
        return redirect(url_for("start"))

    seen = session["seen"]
    if len(seen) >= TOTAL_IMAGES:
        return redirect(url_for("done"))

    remaining = list(set(ALL_IMAGES) - set(seen))
    image = random.choice(remaining)
    session["current_image"] = image
    return render_template("index.html", image=image)

@app.route("/submit", methods=["POST"])
def submit():
    q1 = request.form.get("question1")
    q2 = request.form.get("question2")
    user_id = session.get("user_id", "unknown")
    age = session.get("age", "unknown")
    image = session.get("current_image", "unknown")
    timestamp = datetime.now().isoformat()

    conn = sqlite3.connect("responses.db")
    c = conn.cursor()
    c.execute(
        "INSERT INTO responses (user_id, timestamp, age, image, arousal, valence) VALUES (?, ?, ?, ?, ?, ?)",
        (user_id, timestamp, age, image, q1, q2)
    )
    conn.commit()
    conn.close()

    session["seen"].append(image)
    session.modified = True
    return redirect(url_for("index"))

@app.route("/done")
def done():
    return render_template("done.html")

@app.route("/restart")
def restart():
    session.clear()
    return redirect(url_for("start"))

from flask import Response
import sqlite3

@app.route("/download")
def download_csv():
    conn = sqlite3.connect("responses.db")
    c = conn.cursor()
    c.execute("SELECT * FROM responses")
    data = c.fetchall()
    conn.close()

    # CSV header based on your table fields
    csv_data = "id,user_id,timestamp,age,image,arousal,valence\n"
    for row in data:
        csv_data += ",".join(str(cell) for cell in row) + "\n"

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=responses.csv"}
    )

@app.route("/delete-table")
def delete_table():
    conn = sqlite3.connect("responses.db")
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS responses")
    conn.commit()
    conn.close()
    return "Table 'responses' deleted successfully."    

if __name__ == "__main__":
    app.run(debug=True)
