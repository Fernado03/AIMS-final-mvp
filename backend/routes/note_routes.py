# routes/note_routes.py

from flask import Blueprint, request, jsonify, send_from_directory
import traceback

# Import functions from services and database
from backend.services.speech_service import transcribe_audio_from_gcs
from backend.services.llm_service import generate_assessment_from_notes, generate_plan_from_soap_notes, generate_summary_from_soap_note
from backend.database import get_db_connection, update_note_field, create_note_session_db, get_note_by_id

note_bp = Blueprint('note_routes', __name__)

@note_bp.route('/transcribe', methods=['POST'])
def transcribe_route():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided."}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "Empty filename."}), 400

        transcript_text = transcribe_audio_from_gcs(file, file.filename)
        return jsonify({"text": transcript_text})

    except Exception as e:
        print(f"Error in /transcribe route: {e}\n{traceback.format_exc()}")
        return jsonify({"error": f"Transcription error: {str(e)}"}), 500

@note_bp.route('/create_note_session', methods=['POST'])
def create_note_session_route():
    try:
        result = create_note_session_db()
        return jsonify({"message": "New note session created.", "note_id": result["note_id"]}), 201
    except Exception as e:
        return jsonify({"error": f"Failed to create note session: {e}\n{traceback.format_exc()}"}), 500

@note_bp.route('/update_note_subjective', methods=['POST'])
def update_subjective_route():
    data = request.get_json()
    note_id = data.get('note_id')
    if not note_id: return jsonify({"error": "Missing note_id."}), 400
    
    response, status_code = update_note_field(note_id, data, {"subjective_text": "subjective_text"})
    return jsonify(response), status_code

@note_bp.route('/update_note_objective', methods=['POST'])
def update_objective_route():
    data = request.get_json()
    note_id = data.get('note_id')
    objective_text_to_save = data.get('objective_text')

    if not note_id:
        return jsonify({"error": "Missing note_id."}), 400
    if objective_text_to_save is None:
        return jsonify({"error": "Missing objective_text."}), 400

    conn = None # Initialize conn to None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE notes SET objective_text = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (objective_text_to_save, note_id))
        conn.commit()
        if cursor.rowcount == 0:
            print(f"⚠️ Objective update failed: Note ID {note_id} not found or no update made.")
            return jsonify({"error": "Note not found or no update made for objective text."}), 404
        print(f"💾 Objective text for Note ID {note_id} updated successfully.")
        return jsonify({"message": f"Objective text for Note ID {note_id} updated successfully."}), 200
    except Exception as e:
        print(f"🚨 Database error during objective update for Note ID {note_id}: {e}\n{traceback.format_exc()}")
        return jsonify({"error": f"Database error: {e}"}), 500
    finally:
        if conn:
            conn.close()

@note_bp.route('/api/generate_assessment/<int:note_id>', methods=['GET'])
def generate_assessment_api_route(note_id):
    try:
        note_data = get_note_by_id(note_id)
        if not note_data:
            return jsonify({"error": "Note not found."}), 404

        subjective_text = note_data.get('subjective_text', '')
        objective_text = note_data.get('objective_text', '')

        if not subjective_text.strip() or not objective_text.strip():
            print(f"ℹ️ Missing S or O data for Note ID {note_id} for on-demand assessment generation.")
            return jsonify({"error": "Could not generate assessment. Missing S/O data."}), 500

        print(f"🤖 Attempting to generate assessment on-demand for note ID {note_id}...")
        generated_assessment = generate_assessment_from_notes(subjective_text, objective_text)
        
        if generated_assessment:
            print(f"✅ On-demand assessment generated for Note ID {note_id}.")
            return jsonify({"assessment_text": generated_assessment}), 200
        else:
            print(f"⚠️ On-demand assessment generation failed for Note ID {note_id} (AI error or empty response).")
            return jsonify({"error": "Could not generate assessment. AI error."}), 500

    except Exception as e:
        print(f"🚨 Error in /api/generate_assessment/{note_id}: {e}\n{traceback.format_exc()}")
        return jsonify({"error": f"Server error: {e}"}), 500

@note_bp.route('/update_note_assessment', methods=['POST'])
def update_assessment_route():
    data = request.get_json()
    note_id = data.get('note_id')
    assessment_text_to_save = data.get('assessment_text')

    if not note_id:
        return jsonify({"error": "Missing note_id."}), 400
    if assessment_text_to_save is None:
        return jsonify({"error": "Missing assessment_text."}), 400

    conn = None # Initialize conn to None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE notes SET assessment_text = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (assessment_text_to_save, note_id))
        conn.commit()
        if cursor.rowcount == 0:
            print(f"⚠️ Assessment update failed: Note ID {note_id} not found or no update made.")
            return jsonify({"error": "Note not found or no update made for assessment text."}), 404
        print(f"💾 Assessment text for Note ID {note_id} updated successfully.")
        return jsonify({"message": f"Assessment text for Note ID {note_id} updated successfully."}), 200

    except Exception as e:
        print(f"🚨 Database error during assessment update for Note ID {note_id}: {e}\n{traceback.format_exc()}")
        return jsonify({"error": f"Database error: {e}"}), 500
    finally:
        if conn:
            conn.close()

@note_bp.route('/api/generate_plan/<int:note_id>', methods=['GET'])
def generate_plan_api_route(note_id):
    try:
        note_data = get_note_by_id(note_id)
        if not note_data:
            return jsonify({"error": "Note not found."}), 404

        subjective_text = note_data.get('subjective_text', '')
        objective_text = note_data.get('objective_text', '')
        assessment_text = note_data.get('assessment_text', '')

        if not all([subjective_text.strip(), objective_text.strip(), assessment_text.strip()]):
            missing_fields = []
            if not subjective_text.strip(): missing_fields.append("Subjective")
            if not objective_text.strip(): missing_fields.append("Objective")
            if not assessment_text.strip(): missing_fields.append("Assessment")
            print(f"ℹ️ Missing data for Note ID {note_id} for on-demand plan generation. Missing: {', '.join(missing_fields)}")
            return jsonify({"error": f"Could not generate plan. Missing S/O/A data ({', '.join(missing_fields)} is missing or empty)."}), 500

        print(f"🤖 Attempting to generate plan on-demand for note ID {note_id}...")
        generated_plan_text = generate_plan_from_soap_notes(subjective_text, objective_text, assessment_text)
        
        if generated_plan_text is not None:
            print(f"✅ On-demand plan generated for Note ID {note_id}.")
            return jsonify({"plan_text": generated_plan_text}), 200
        else:
            print(f"⚠️ On-demand plan generation failed for Note ID {note_id} (AI error or empty response).")
            return jsonify({"error": "Could not generate plan. AI error or empty response."}), 500

    except Exception as e:
        print(f"🚨 Error in /api/generate_plan/{note_id}: {e}\n{traceback.format_exc()}")
        return jsonify({"error": f"Server error: {e}"}), 500

@note_bp.route('/update_note_plan', methods=['POST'])
def update_plan_route():
    data = request.get_json()
    note_id = data.get('note_id')
    plan_text_to_save = data.get('plan_text')

    if not note_id:
        return jsonify({"error": "Missing note_id."}), 400
    if plan_text_to_save is None:
        return jsonify({"error": "Missing plan_text."}), 400

    conn = None # Initialize conn to None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE notes SET plan_text = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (plan_text_to_save, note_id))
        conn.commit()
        if cursor.rowcount == 0:
            print(f"⚠️ Plan update failed: Note ID {note_id} not found or no update made.")
            return jsonify({"error": "Note not found or no update made for plan text."}), 404
        print(f"💾 Plan text for Note ID {note_id} updated successfully.")
        return jsonify({"message": f"Plan text for Note ID {note_id} updated successfully."}), 200

    except Exception as e:
        print(f"🚨 Database error during plan update for Note ID {note_id}: {e}\n{traceback.format_exc()}")
        return jsonify({"error": f"Database error: {e}"}), 500
    finally:
        if conn:
            conn.close()

@note_bp.route('/api/generate_summary/<int:note_id>', methods=['GET'])
def generate_summary_api_route(note_id):
    try:
        note_data = get_note_by_id(note_id)
        if not note_data:
            return jsonify({"error": "Note not found."}), 404

        subjective_text = note_data.get('subjective_text', '')
        objective_text = note_data.get('objective_text', '')
        assessment_text = note_data.get('assessment_text', '')
        plan_text = note_data.get('plan_text', '')

        if not all([subjective_text.strip(), objective_text.strip(), assessment_text.strip(), plan_text.strip()]):
            missing_fields = []
            if not subjective_text.strip(): missing_fields.append("Subjective")
            if not objective_text.strip(): missing_fields.append("Objective")
            if not assessment_text.strip(): missing_fields.append("Assessment")
            if not plan_text.strip(): missing_fields.append("Plan")
            print(f"ℹ️ Missing data for Note ID {note_id} for on-demand summary generation. Missing: {', '.join(missing_fields)}")
            return jsonify({"error": f"Could not generate summary. Missing S/O/A/P data ({', '.join(missing_fields)} is missing or empty)."}), 500

        print(f"🤖 Attempting to generate summary on-demand for note ID {note_id}...")
        generated_summary_text = generate_summary_from_soap_note(subjective_text, objective_text, assessment_text, plan_text)
        
        if generated_summary_text is not None:
            print(f"✅ On-demand summary generated for Note ID {note_id}.")
            return jsonify({"summary_text": generated_summary_text}), 200
        else:
            print(f"⚠️ On-demand summary generation failed for Note ID {note_id} (AI error or empty response).")
            return jsonify({"error": "Could not generate summary. Missing S/O/A/P data or AI error."}), 500

    except Exception as e:
        print(f"🚨 Error in /api/generate_summary/{note_id}: {e}\n{traceback.format_exc()}")
        return jsonify({"error": f"Server error: {e}"}), 500

@note_bp.route('/get_note_data/<int:note_id>', methods=['GET'])
def get_note_route(note_id):
    try:
        note = get_note_by_id(note_id)
        if note:
            return jsonify(note)
        else:
            return jsonify({"error": "Note not found"}), 404
    except Exception as e:
        return jsonify({"error": f"Failed to fetch note: {e}\n{traceback.format_exc()}"}), 500