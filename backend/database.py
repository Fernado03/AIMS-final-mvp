# database.py

import sqlite3
import os
import traceback
from backend.config import DATABASE_NAME, DATABASE_PATH

def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row # To access columns by name
    return conn

def init_db():
    conn = None # Initialize conn
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subjective_text TEXT,
                objective_text TEXT,
                assessment_text TEXT,
                plan_text TEXT,
                summary_text TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # Check if updated_at trigger exists, if not, create it
        cursor.execute('''
            SELECT name FROM sqlite_master WHERE type='trigger' AND name='update_notes_updated_at';
        ''')
        if cursor.fetchone() is None:
            cursor.execute('''
                CREATE TRIGGER update_notes_updated_at
                AFTER UPDATE ON notes
                FOR EACH ROW
                BEGIN
                    UPDATE notes SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
                END;
            ''')
        conn.commit()
        print(f"Database '{DATABASE_NAME}' initialized successfully at {DATABASE_PATH}")
    except Exception as e:
        print(f"Error initializing database: {e}\n{traceback.format_exc()}")
    finally:
        if conn:
            conn.close()

def update_note_field(note_id, data_dict, field_map):
    conn = get_db_connection()
    cursor = conn.cursor()
    fields_to_update = []
    values_to_update = []
    for key, column_name in field_map.items():
        if key in data_dict:
            fields_to_update.append(f"{column_name} = ?")
            values_to_update.append(data_dict[key])

    if not fields_to_update:
        conn.close()
        return {"error": "No valid fields provided for update."}, 400 # Return dict and status

    values_to_update.append(note_id)
    sql = f"UPDATE notes SET {', '.join(fields_to_update)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?"

    try:
        cursor.execute(sql, tuple(values_to_update))
        conn.commit()
        if cursor.rowcount == 0:
            print(f"⚠️ Note ID {note_id} not found or no update made.")
            return {"error": "Note not found or no update made."}, 404
        print(f"💾 Note ID {note_id} updated. Fields: {', '.join(field_map.values())}")
        return {"message": f"Note ID {note_id} updated successfully."}, 200
    except Exception as e:
        print(f"🚨 Database error updating note: {e}\n{traceback.format_exc()}")
        return {"error": f"Database error updating note: {e}\n{traceback.format_exc()}"}, 500
    finally:
        if conn:
            conn.close()

# You might move create_note_session and get_note_data here as well
def create_note_session_db():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO notes (subjective_text, objective_text, assessment_text, plan_text, summary_text) VALUES (?, ?, ?, ?, ?)",
                         ("", "", "", "", ""))
        conn.commit()
        new_note_id = cursor.lastrowid
        print(f"✨ New note session created with ID: {new_note_id}")
        return {"note_id": new_note_id} # Return dict
    except Exception as e:
        print(f"Failed to create note session: {e}\n{traceback.format_exc()}")
        raise # Re-raise to be caught by route

def get_note_by_id(note_id):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
        note = cursor.fetchone()
        if note:
            return dict(note)
        else:
            return None # Return None if not found
    except Exception as e:
        print(f"Failed to fetch note: {e}\n{traceback.format_exc()}")
        raise # Re-raise to be caught by route
    finally:
        if conn:
            conn.close()