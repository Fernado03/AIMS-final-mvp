# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

AIMS (AI Medical Scribe) is a clinical documentation assistant that leverages AI to help healthcare professionals generate structured SOAP notes. The system combines **local voice transcription (OpenAI Whisper)** with an OpenAI-compatible LLM and a RAG pipeline over Malaysian clinical practice guidelines (MiniLM + CrossEncoder).

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
# Then edit .env with LLM_API_KEY (and optional LLM_BASE_URL / LLM_MODEL)
```

### Database Operations
```bash
# Local Mongo: docker start aims-mongo
# Database is initialized on app start (MONGO_URI / DATABASE_NAME)
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
- MongoDB for clinical notes storage
- AI services integration (OpenAI Whisper for local STT, OpenAI-compatible LLM)
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
5. **Data Persistence**: All note data stored in MongoDB with timestamp tracking

### Database Schema

**Notes collection** (MongoDB `aims_medical_scribe`):
- `_id`: ObjectId
- `subjective_text`, `objective_text`, `assessment_text`, `plan_text`, `summary_text`: SOAP sections
- `created_at`, `updated_at`: timestamps

## Critical Integration Points

### AI Services
- **Whisper (OpenAI)**: Local speech-to-text transcription (`services/speech_service.py`)
  - Runs locally on your machine
  - No cloud upload required
  - HIPAA-compliant privacy
- **LLM:** OpenAI-compatible API for clinical text generation (`services/llm_service.py`)
  - Default: `glm-5.3-flash` at `https://api.hcnsec.cn/v1`
  - Requires `LLM_API_KEY`

### Configuration Management
- Environment variables loaded via `python-dotenv`
- Service configurations centralized in `backend/config.py`
- Required for LLM: `LLM_API_KEY`, optional `LLM_BASE_URL` / `LLM_MODEL`
- Optional for STT: `WHISPER_MODEL` (default: medium), `WHISPER_LANGUAGE` (default: en)
- Database: `MONGO_URI` (default `mongodb://127.0.0.1:27017`), `DATABASE_NAME` (default `aims_medical_scribe`)

### RAG Knowledge Base
- Clinical Practice Guidelines (CPGs) retrieved with MiniLM cosine + CrossEncoder rerank
- Integration with LLM prompts via `backend/rag/rag_service.py`
- Cache: `backend/rag/corpus/clinical_practical_guide/minilm_l6_v2_embeddings.npz`

## File Organization Patterns

### Backend Structure
- `app.py`: Flask application entry point with route definitions
- `database.py`: MongoDB operations
- `routes/`: API endpoint definitions grouped by functionality
- `services/`: External service integrations (Whisper STT, OpenAI-compatible LLM)
- `rag/`: Knowledge base and prompt management for clinical context

### Frontend Structure
- Root HTML files: Each SOAP section has dedicated page
- `public/`: Static assets (images, backgrounds)
- JavaScript in `script.js` for SOAP workflow

### Data Processing
- `rag_cpg_pipeline/`: Standalone processing for clinical guidelines
- `input_pdfs/`: Clinical practice guideline source documents
- `output_data/`: Processed text, chunks, and embeddings in stages

## Development Guidelines

### API Patterns
- RESTful endpoints for CRUD operations on notes
- Streaming endpoints for Assessment / Plan (`/api/stream_{section}/{note_id}`); Summary is `/api/generate_summary/{note_id}`
- Error handling with structured JSON responses
- Database connection management with proper cleanup

### AI Integration
- Prompt templates live in `backend/services/llm_service.py`
- RAG context injection for clinically relevant responses
- Graceful degradation when AI services unavailable
- Response validation for medical content structure

### Environment Configuration
- Development uses local Docker Mongo (`aims-mongo`)
- LLM API key required for AI features (`LLM_API_KEY`)
- Environment-specific settings via `.env` file
- Windows PowerShell compatibility for development commands

## Troubleshooting Notes

- Database issues: `docker start aims-mongo` (check `MONGO_URI` in `.env`)
- LLM errors: Verify `LLM_API_KEY` / `LLM_BASE_URL` in `.env`
- Audio transcription: First run downloads Whisper model (~1.5GB for medium model)
- Whisper model location: `~/.cache/whisper/` (Linux/Mac) or `C:\Users\<user>\.cache\whisper\` (Windows)
- FFmpeg required: Install with `choco install ffmpeg` (Windows) or `brew install ffmpeg` (Mac)
- RAG context: Clinical guidelines must be processed before use
- Out of memory: Use smaller Whisper model (`WHISPER_MODEL=small` or `tiny`)

## Project Context

This is a clinical documentation system designed for healthcare environments. The codebase prioritizes medical accuracy through AI-assisted generation enhanced by clinical practice guidelines. The SOAP note workflow reflects standard medical documentation practices.