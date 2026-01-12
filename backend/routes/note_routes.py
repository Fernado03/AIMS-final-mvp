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
    print("\n" + "="*50)
    print("🎤 TRANSCRIBE ROUTE CALLED")
    print("="*50)
    try:
        if 'file' not in request.files:
            print("❌ No file in request")
            return jsonify({"error": "No file provided."}), 400

        file = request.files['file']
        print(f"✅ File received: {file.filename}")
        
        if file.filename == '':
            print("❌ Empty filename")
            return jsonify({"error": "Empty filename."}), 400

        print(f"📝 Starting transcription for: {file.filename}")
        transcript_text = transcribe_audio_from_gcs(file, file.filename)
        print(f"✅ Transcription complete: {transcript_text[:100]}...")
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

    try:
        response, status_code = update_note_field(note_id, {"objective_text": objective_text_to_save}, {"objective_text": "objective_text"})
        return jsonify(response), status_code
    except Exception as e:
        print(f"🚨 Error in /update_note_objective: {e}\n{traceback.format_exc()}")
        return jsonify({"error": f"Server error: {e}"}), 500

@note_bp.route('/api/generate_assessment/<note_id>', methods=['GET'])
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

    try:
        response, status_code = update_note_field(note_id, {"assessment_text": assessment_text_to_save}, {"assessment_text": "assessment_text"})
        return jsonify(response), status_code
    except Exception as e:
        print(f"🚨 Error in /update_note_assessment: {e}\n{traceback.format_exc()}")
        return jsonify({"error": f"Server error: {e}"}), 500

@note_bp.route('/api/generate_plan/<note_id>', methods=['GET'])
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

    try:
        response, status_code = update_note_field(note_id, {"plan_text": plan_text_to_save}, {"plan_text": "plan_text"})
        return jsonify(response), status_code
    except Exception as e:
        print(f"🚨 Error in /update_note_plan: {e}\n{traceback.format_exc()}")
        return jsonify({"error": f"Server error: {e}"}), 500

@note_bp.route('/api/generate_summary/<note_id>', methods=['GET'])
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

@note_bp.route('/get_note_data/<note_id>', methods=['GET'])
def get_note_route(note_id):
    try:
        note = get_note_by_id(note_id)
        if note:
            return jsonify(note)
        else:
            return jsonify({"error": "Note not found"}), 404
    except Exception as e:
        return jsonify({"error": f"Failed to fetch note: {e}\n{traceback.format_exc()}"}), 500

# --- Streaming Endpoints ---

from flask import Response, stream_with_context
from backend.services.llm_service import stream_assessment_from_notes, stream_plan_from_soap_notes, stream_summary_from_soap_note

@note_bp.route('/api/stream_assessment/<note_id>', methods=['GET'])
def stream_assessment_route(note_id):
    note_data = get_note_by_id(note_id)
    if not note_data:
        return jsonify({"error": "Note not found."}), 404

    subjective = note_data.get('subjective_text', '')
    objective = note_data.get('objective_text', '')

    if not subjective.strip() or not objective.strip():
        return jsonify({"error": "Missing Subjective or Objective data."}), 400

    def generate():
        for chunk in stream_assessment_from_notes(subjective, objective):
            yield chunk

    return Response(stream_with_context(generate()), mimetype='text/event-stream')

@note_bp.route('/api/stream_plan/<note_id>', methods=['GET'])
def stream_plan_route(note_id):
    note_data = get_note_by_id(note_id)
    if not note_data:
        return jsonify({"error": "Note not found."}), 404

    subjective = note_data.get('subjective_text', '')
    objective = note_data.get('objective_text', '')
    assessment = note_data.get('assessment_text', '')

    if not all([subjective.strip(), objective.strip(), assessment.strip()]):
        return jsonify({"error": "Missing S/O/A data."}), 400

    def generate():
        for chunk in stream_plan_from_soap_notes(subjective, objective, assessment):
            yield chunk

    return Response(stream_with_context(generate()), mimetype='text/event-stream')

@note_bp.route('/api/stream_summary/<note_id>', methods=['GET'])
def stream_summary_route(note_id):
    note_data = get_note_by_id(note_id)
    if not note_data:
        return jsonify({"error": "Note not found."}), 404

    s = note_data.get('subjective_text', '')
    o = note_data.get('objective_text', '')
    a = note_data.get('assessment_text', '')
    p = note_data.get('plan_text', '')

    if not all([s.strip(), o.strip(), a.strip(), p.strip()]):
        return jsonify({"error": "Missing S/O/A/P data."}), 400

    def generate():
        for chunk in stream_summary_from_soap_note(s, o, a, p):
            yield chunk

    return Response(stream_with_context(generate()), mimetype='text/event-stream')