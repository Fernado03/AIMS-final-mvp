from flask import Flask, send_from_directory
import os
from backend.database import init_db
from backend.routes.note_routes import note_bp

_front = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
app = Flask(__name__, static_folder=_front, static_url_path="/")
app.register_blueprint(note_bp)


@app.route("/")
def index():
    return send_from_directory(_front, "index.html")


if __name__ == "__main__":
    init_db()
    app.run(debug=True, use_reloader=False, host="0.0.0.0", port=5000)
