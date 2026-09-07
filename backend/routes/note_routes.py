from flask import Blueprint, request, jsonify, Response, stream_with_context
import traceback
from backend.services.speech_service import transcribe_audio
from backend.services.llm_service import (
    generate_summary_from_soap_note,
    stream_assessment_from_notes,
    stream_plan_from_soap_notes,
)
from backend.database import update_note_field, create_note_session_db, get_note_by_id

note_bp = Blueprint("note_routes", __name__)


@note_bp.route("/transcribe", methods=["POST"])
def transcribe_route():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file provided."}), 400
        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "Empty filename."}), 400
        return jsonify({"text": transcribe_audio(file, file.filename)})
    except Exception as e:
        print(f"Error in /transcribe route: {e}\n{traceback.format_exc()}")
        return jsonify({"error": f"Transcription error: {str(e)}"}), 500


@note_bp.route("/create_note_session", methods=["POST"])
def create_note_session_route():
    try:
        result = create_note_session_db()
        return jsonify({"message": "New note session created.", "note_id": result["note_id"]}), 201
    except Exception as e:
        return jsonify({"error": f"Failed to create note session: {e}\n{traceback.format_exc()}"}), 500


@note_bp.route("/update_note_subjective", methods=["POST"])
def update_subjective_route():
    data = request.get_json()
    note_id = data.get("note_id")
    if not note_id:
        return jsonify({"error": "Missing note_id."}), 400
    response, status_code = update_note_field(note_id, data, {"subjective_text": "subjective_text"})
    return jsonify(response), status_code


@note_bp.route("/update_note_objective", methods=["POST"])
def update_objective_route():
    data = request.get_json()
    note_id = data.get("note_id")
    objective_text_to_save = data.get("objective_text")
    if not note_id:
        return jsonify({"error": "Missing note_id."}), 400
    if objective_text_to_save is None:
        return jsonify({"error": "Missing objective_text."}), 400
    try:
        response, status_code = update_note_field(
            note_id, {"objective_text": objective_text_to_save}, {"objective_text": "objective_text"}
        )
        return jsonify(response), status_code
    except Exception as e:
        print(f"🚨 Error in /update_note_objective: {e}\n{traceback.format_exc()}")
        return jsonify({"error": f"Server error: {e}"}), 500


@note_bp.route("/update_note_assessment", methods=["POST"])
def update_assessment_route():
    data = request.get_json()
    note_id = data.get("note_id")
    assessment_text_to_save = data.get("assessment_text")
    if not note_id:
        return jsonify({"error": "Missing note_id."}), 400
    if assessment_text_to_save is None:
        return jsonify({"error": "Missing assessment_text."}), 400
    try:
        response, status_code = update_note_field(
            note_id, {"assessment_text": assessment_text_to_save}, {"assessment_text": "assessment_text"}
        )
        return jsonify(response), status_code
    except Exception as e:
        print(f"🚨 Error in /update_note_assessment: {e}\n{traceback.format_exc()}")
        return jsonify({"error": f"Server error: {e}"}), 500


@note_bp.route("/update_note_plan", methods=["POST"])
def update_plan_route():
    data = request.get_json()
    note_id = data.get("note_id")
    plan_text_to_save = data.get("plan_text")
    if not note_id:
        return jsonify({"error": "Missing note_id."}), 400
    if plan_text_to_save is None:
        return jsonify({"error": "Missing plan_text."}), 400
    try:
        response, status_code = update_note_field(
            note_id, {"plan_text": plan_text_to_save}, {"plan_text": "plan_text"}
        )
        return jsonify(response), status_code
    except Exception as e:
        print(f"🚨 Error in /update_note_plan: {e}\n{traceback.format_exc()}")
        return jsonify({"error": f"Server error: {e}"}), 500


@note_bp.route("/api/generate_summary/<note_id>", methods=["GET"])
def generate_summary_api_route(note_id):
    try:
        note_data = get_note_by_id(note_id)
        if not note_data:
            return jsonify({"error": "Note not found."}), 404
        s = note_data.get("subjective_text", "")
        o = note_data.get("objective_text", "")
        a = note_data.get("assessment_text", "")
        p = note_data.get("plan_text", "")
        if not all([s.strip(), o.strip(), a.strip(), p.strip()]):
            missing = [n for n, t in (("Subjective", s), ("Objective", o), ("Assessment", a), ("Plan", p)) if not t.strip()]
            return jsonify({"error": f"Could not generate summary. Missing: {', '.join(missing)}."}), 500
        generated = generate_summary_from_soap_note(s, o, a, p)
        if generated is not None:
            return jsonify({"summary_text": generated}), 200
        return jsonify({"error": "Could not generate summary. AI error."}), 500
    except Exception as e:
        print(f"🚨 Error in /api/generate_summary/{note_id}: {e}\n{traceback.format_exc()}")
        return jsonify({"error": f"Server error: {e}"}), 500


@note_bp.route("/get_note_data/<note_id>", methods=["GET"])
def get_note_route(note_id):
    try:
        note = get_note_by_id(note_id)
        if note:
            return jsonify(note)
        return jsonify({"error": "Note not found"}), 404
    except Exception as e:
        return jsonify({"error": f"Failed to fetch note: {e}\n{traceback.format_exc()}"}), 500


@note_bp.route("/api/stream_assessment/<note_id>", methods=["GET"])
def stream_assessment_route(note_id):
    note_data = get_note_by_id(note_id)
    if not note_data:
        return jsonify({"error": "Note not found."}), 404
    subjective = note_data.get("subjective_text", "")
    objective = note_data.get("objective_text", "")
    if not subjective.strip() or not objective.strip():
        return jsonify({"error": "Missing Subjective or Objective data."}), 400
    return Response(
        stream_with_context(stream_assessment_from_notes(subjective, objective)),
        mimetype="text/event-stream",
    )


@note_bp.route("/api/stream_plan/<note_id>", methods=["GET"])
def stream_plan_route(note_id):
    note_data = get_note_by_id(note_id)
    if not note_data:
        return jsonify({"error": "Note not found."}), 404
    subjective = note_data.get("subjective_text", "")
    objective = note_data.get("objective_text", "")
    assessment = note_data.get("assessment_text", "")
    if not all([subjective.strip(), objective.strip(), assessment.strip()]):
        return jsonify({"error": "Missing S/O/A data."}), 400
    return Response(
        stream_with_context(stream_plan_from_soap_notes(subjective, objective, assessment)),
        mimetype="text/event-stream",
    )
