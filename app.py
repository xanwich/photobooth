from flask import (
    Flask,
    render_template,
    Response,
    redirect,
    url_for,
    make_response,
    jsonify,
)
import os
import sys
from datetime import datetime
from time import sleep
import glob
from threading import Thread


from .image import Booth
from .camera import Camera

app = Flask(__name__)

os.makedirs("images", exist_ok=True)
cam = Camera()
current_text = "init"
capture_in_progress = False


@app.route("/")
def index():
    global current_text
    current_text = '<h1><a href="/capture">start</a></h1>'
    return render_template("index.html")


@app.route("/capture")
def capture():
    if not capture_in_progress:
        th = Thread(target=run_capture, args=())
        th.start()
    return render_template("index.html")


@app.route("/status")
def status():
    global current_text
    print(current_text)
    return current_text


@app.route("/print")
def show_print_screen():
    global current_text
    current_text = '<h1>printing!!!</h1><h1><a href="/capture">restart</a></h1>'
    return render_template("index.html")


def run_capture():
    global current_text
    global capture_in_progress
    capture_in_progress = True
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")
    image_dir = os.path.join("images", timestamp, "raw")
    os.makedirs(image_dir)
    current_text = "<h1>get ready!</h1>"
    sleep(3)
    for _ in range(4):
        for i in range(3, 0, -1):
            current_text = f"<h1>{str(i)}...</h1>"
            sleep(1)
        current_text = "<h1>smile!!!</h1>(downloading image...)"
        sleep(1)
        cam.capture()
    cam.download_n_most_recent_images(image_dir)
    upload_and_print()
    capture_in_progress = False


def upload_and_print():
    global current_text
    image_dir = max(glob.glob("images/*T*"))
    b = Booth(image_dir)
    current_text = "processing..."
    b.run()
    current_text = "done"
    current_text = '<h1>printing!!!</h1><h1><a href="/capture">restart</a></h1>'


if __name__ == "__main__":
    app.run(debug=True)
