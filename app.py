from flask import Flask, render_template, request, redirect, url_for, session
import os, random
from datetime import datetime

app = Flask(__name__)
app.secret_key = "your_secret_key"

IMAGE_FOLDER = "static/images"
ALL_IMAGES = os.listdir(IMAGE_FOLDER)
TOTAL_IMAGES = len(ALL_IMAGES)

@app.route("/start", methods=["GET", "POST"])
def start():
    if request.method == "POST":
        age = request.form.get("age")
        if age and age.isdigit():
            session["age"] = int(age)
            session["seen"] = []
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
    age = session.get("age", "unknown")
    image = session.get("current_image", "unknown")

    with open("responses.csv", "a") as f:
        f.write(f"{datetime.now()},{age},{image},{q1},{q2}\n")

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

if __name__ == "__main__":
    app.run(debug=True)