# database.py

import os
import traceback
from datetime import datetime
from pymongo import MongoClient
from bson.objectid import ObjectId
from backend.config import MONGO_URI, DATABASE_NAME

_path = os.path.dirname(os.path.abspath(__file__))

def get_db_connection():
    """Returns a MongoDB database object."""
    try:
        client = MongoClient(MONGO_URI)
        db = client[DATABASE_NAME]
        return db
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        return None

def init_db():
    """
    Initializes the database. 
    For MongoDB, collections are created lazily, so we just check connectivity.
    """
    try:
        db = get_db_connection()
        # Verify connection
        db.command('ping')
        print(f"✅ MongoDB '{DATABASE_NAME}' connected successfully.")
    except Exception as e:
        print(f"⚠️ Error initializing MongoDB connection: {e}\n{traceback.format_exc()}")
        print(f"Please check your MONGO_URI in .env")

def update_note_field(note_id, data_dict, field_map):
    """
    Updates specific fields in a note document.
    """
    try:
        db = get_db_connection()
        collection = db.notes
        
        update_fields = {}
        for key, column_name in field_map.items():
            if key in data_dict:
                update_fields[column_name] = data_dict[key]

        if not update_fields:
            return {"error": "No valid fields provided for update."}, 400

        update_fields["updated_at"] = datetime.utcnow()

        result = collection.update_one(
            {"_id": ObjectId(note_id)},
            {"$set": update_fields}
        )

        if result.matched_count == 0:
            print(f"⚠️ Note ID {note_id} not found.")
            return {"error": "Note not found."}, 404
        
        print(f"💾 Note ID {note_id} updated. Fields: {', '.join(field_map.values())}")
        return {"message": f"Note ID {note_id} updated successfully."}, 200

    except Exception as e:
        print(f"🚨 Database error updating note: {e}\n{traceback.format_exc()}")
        return {"error": f"Database error: {str(e)}"}, 500

def create_note_session_db():
    """
    Creates a new note document with empty fields.
    """
    try:
        db = get_db_connection()
        collection = db.notes
        
        new_note = {
            "subjective_text": "",
            "objective_text": "",
            "assessment_text": "",
            "plan_text": "",
            "summary_text": "",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = collection.insert_one(new_note)
        new_note_id = str(result.inserted_id)
        
        print(f"✨ New note session created with ID: {new_note_id}")
        return {"note_id": new_note_id}

    except Exception as e:
        print(f"Failed to create note session: {e}\n{traceback.format_exc()}")
        raise

def get_note_by_id(note_id):
    """
    Retrieves a note document by ID.
    """
    try:
        db = get_db_connection()
        collection = db.notes
        
        note = collection.find_one({"_id": ObjectId(note_id)})
        
        if note:
            # Convert ObjectId and datetime to string/isoformat for JSON serialization
            note["id"] = str(note["_id"])
            del note["_id"]
            if "created_at" in note:
                note["created_at"] = note["created_at"].isoformat()
            if "updated_at" in note:
                note["updated_at"] = note["updated_at"].isoformat()
            return note
        else:
            return None

    except Exception as e:
        print(f"Failed to fetch note: {e}\n{traceback.format_exc()}")
        raise