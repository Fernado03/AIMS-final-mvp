# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

AIMS (AI Medical Scribe) is a clinical documentation assistant that leverages AI to help healthcare professionals generate structured SOAP notes. The system combines **local voice transcription (OpenAI Whisper)** with AI-assisted content generation using Google Vertex AI (Gemini model) and includes a RAG (Retrieval-Augmented Generation) pipeline for clinical practice guidelines.

## Development Commands

### Starting the Application
```bash
# Start the backend server
python -m backend.app
# Or from root directory
cd backend && python app.py

# Access the application at http://localhost:5000/
```

### Environment Setup
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Windows Command Prompt:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment configuration
cp .env.example .env
# Then edit .env with your Google Cloud credentials
```

### Database Operations
```bash
# Reset database (delete notes_main.db to start fresh)
# The database is automatically initialized when the app starts
```

### RAG Pipeline (Optional)
```bash
# Process clinical guidelines for RAG
cd rag_cpg_pipeline
python scripts/step_01_extract_text.py
python scripts/step_02_clean_text.py
python scripts/step_03_chunk_text.py
python scripts/step_04_embed_chunks.py
```

## Architecture Overview

### Three-Tier Architecture

**Backend (Python/Flask)**
- Flask web server serving API endpoints and static files
- Database layer with SQLite for clinical notes storage
- AI services integration (OpenAI Whisper for local STT, Vertex AI for LLM)
- RAG system for clinical guidelines retrieval

**Frontend (HTML/CSS/JavaScript)**
- Multi-page SOAP note workflow interface
- Voice recording integration with backend transcription
- Real-time AI suggestion display
- Progressive form completion (Subjective → Objective → Assessment → Plan → Summary)

**RAG Pipeline (Standalone)**
- PDF processing of clinical practice guidelines
- Text extraction, cleaning, and chunking
- Embedding generation and storage
- Clinical context retrieval for AI generation

### Key Data Flow

1. **Voice Input**: Frontend captures audio → Backend transcribes locally via Whisper (no cloud upload)
2. **Note Creation**: Session management creates unique note IDs for each patient encounter
3. **AI Generation**: Each SOAP section can trigger AI-assisted generation using accumulated context
4. **RAG Enhancement**: Clinical guidelines provide context for more accurate AI responses
5. **Data Persistence**: All note data stored in SQLite with timestamp tracking

### Database Schema

**Notes Table**:
- `id`: Primary key (auto-increment)
- `subjective_text`, `objective_text`, `assessment_text`, `plan_text`, `summary_text`: SOAP sections
- `created_at`, `updated_at`: Timestamps with auto-update triggers

## Critical Integration Points

### AI Services
- **Whisper (OpenAI)**: Local speech-to-text transcription (`services/speech_service.py`)
  - Runs locally on your machine
  - No cloud upload required
  - HIPAA-compliant privacy
- **Vertex AI**: LLM integration for clinical text generation (`services/llm_service.py`)
  - Requires Google Cloud credentials
  - Used only for AI-assisted note generation

### Configuration Management
- Environment variables loaded via `python-dotenv`
- Service configurations centralized in `backend/config.py`
- Required for LLM: `GOOGLE_APPLICATION_CREDENTIALS`, `VERTEX_AI_PROJECT_ID`
- Optional for STT: `WHISPER_MODEL` (default: medium), `WHISPER_LANGUAGE` (default: en)
- Database: `DATABASE_NAME` (default: notes_main.db)

### RAG Knowledge Base
- Clinical Practice Guidelines (CPGs) processed into embeddings
- Vector similarity search for relevant medical context
- Integration with LLM prompts via `backend/rag/knowledge_base_service.py`

## File Organization Patterns

### Backend Structure
- `app.py`: Flask application entry point with route definitions
- `database.py`: SQLite operations and schema management
- `routes/`: API endpoint definitions grouped by functionality
- `services/`: External service integrations (Whisper STT, Vertex AI LLM)
- `rag/`: Knowledge base and prompt management for clinical context

### Frontend Structure
- Root HTML files: Each SOAP section has dedicated page
- `components/`: Reusable UI elements
- `public/`: Static assets (images, backgrounds)
- JavaScript embedded in HTML files for page-specific functionality

### Data Processing
- `rag_cpg_pipeline/`: Standalone processing for clinical guidelines
- `input_pdfs/`: Clinical practice guideline source documents
- `output_data/`: Processed text, chunks, and embeddings in stages

## Development Guidelines

### API Patterns
- RESTful endpoints for CRUD operations on notes
- Separate endpoints for AI generation (`/api/generate_{section}/{note_id}`)
- Error handling with structured JSON responses
- Database connection management with proper cleanup

### AI Integration
- Prompt engineering for medical contexts in `rag/prompt_service.py`
- RAG context injection for clinically relevant responses
- Graceful degradation when AI services unavailable
- Response validation for medical content structure

### Environment Configuration
- Development uses local SQLite database
- Google Cloud credentials required for AI features
- Environment-specific settings via `.env` file
- Windows PowerShell compatibility for development commands

## Troubleshooting Notes

- Database issues: Delete `backend/notes_main.db` to reset
- Vertex AI errors: Verify `GOOGLE_APPLICATION_CREDENTIALS` path and project ID
- Audio transcription: First run downloads Whisper model (~1.5GB for medium model)
- Whisper model location: `~/.cache/whisper/` (Linux/Mac) or `C:\Users\<user>\.cache\whisper\` (Windows)
- FFmpeg required: Install with `choco install ffmpeg` (Windows) or `brew install ffmpeg` (Mac)
- RAG context: Clinical guidelines must be processed before use
- Out of memory: Use smaller Whisper model (`WHISPER_MODEL=small` or `tiny`)

## Project Context

This is a clinical documentation system designed for healthcare environments. The codebase prioritizes medical accuracy through AI-assisted generation enhanced by clinical practice guidelines. The SOAP note workflow reflects standard medical documentation practices.