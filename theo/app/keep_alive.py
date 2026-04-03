from flask import Flask
from threading import Thread
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "Theo is alive and running!"

def run():
    # Render assigns a dynamic PORT, we must listen to it
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

def keep_alive():
    t = Thread(target=run, daemon=True, name="keep-alive-server")
    t.start()
