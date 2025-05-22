# app.py

from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS
import os
import sys
import traceback
from dotenv import load_dotenv

# Import your database and route modules
load_dotenv()
from backend.database import init_db
from backend.routes.note_routes import note_bp
from backend.services.llm_service import gemini_model # To check if model loaded

app = Flask(__name__,
    static_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend')),
    static_url_path='/',
    template_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend')))
CORS(app) # Enable CORS for your Flask app

# Register blueprints
app.register_blueprint(note_bp)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/subjective')
def subjective():
    return render_template('subjective.html')

@app.route('/objective')
def objective():
    return render_template('objective.html')

@app.route('/assessment')
def assessment():
    return render_template('assessment.html')

@app.route('/plan')
def plan():
    return render_template('plan.html')

@app.route('/summary')
def summary():
    return render_template('summary.html')


if __name__ == '__main__':
    init_db()
    if not os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
        print("⚠️ WARNING: GOOGLE_APPLICATION_CREDENTIALS environment variable not set.")
    app.run(debug=True, host='0.0.0.0', port=5000)