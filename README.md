# AIMS Medical Scribe - AI-Powered Clinical Documentation

AIMS (AI Medical Scribe) is an advanced clinical documentation assistant leveraging large language models (LLMs) to help healthcare professionals generate accurate, structured SOAP notes. The application combines real-time voice transcription with AI-assisted content generation powered by Google Vertex AI (Gemini model), providing intelligent suggestions throughout the documentation workflow.

## Table of Contents
- [System Components](#system-components)
  - [Backend](#backend)
  - [Frontend](#frontend)
  - [RAG CPG Pipeline](#rag-cpg-pipeline)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Setup Instructions](#setup-instructions)
- [Usage Workflow](#usage-workflow)
- [Project Structure](#project-structure)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)
- [Support](#support)

## System Components

### Backend
Located in `backend/` directory, provides the AI/LLM processing core including:
- Voice-to-text transcription (Google Cloud Speech-to-Text)
- LLM-powered clinical note generation (Google Vertex AI Gemini)
- API endpoints for frontend integration
- Database operations for clinical data

### Frontend
Located in `frontend/` directory, contains the clinical documentation interface with:
- Real-time AI suggestions
- Interactive SOAP note workflow
- Voice recording integration

### RAG CPG Pipeline (Optional)
The RAG (Retrieval-Augmented Generation) CPG (Clinical Practice Guidelines) pipeline enhances the AI system by providing structured medical guideline knowledge for reference during documentation.

## Features

### AI-Powered Documentation
- **Voice Transcription:** Real-time speech-to-text powered by Google Cloud Speech-to-Text API
- **AI-Assisted Generation:** Context-aware clinical suggestions using Google Vertex AI (Gemini model) for:
  - Differential diagnoses
  - Treatment plan recommendations
  - Clinical documentation refinement
- **Clinical Summary:** Automated generation of structured patient summaries with LLM post-processing

### Backend Services
- Voice transcription service
- AI generation service
- Database operations
- API endpoints for frontend integration

### Frontend Components
- SOAP note workflow components
- Voice recording interface
- Clinical documentation forms
- AI suggestion display components

### Technical Features
- **Web-Based Interface:** Responsive design for desktop use
- **Data Persistence:** Patient notes stored securely in local database
- **Real-Time Processing:** Immediate feedback during note creation

## Technology Stack

### Core AI Components
- **Large Language Model:** Google Vertex AI (Gemini model) for clinical text generation
- **Speech Recognition:** Google Cloud Speech-to-Text API for voice transcription
- **Natural Language Processing:** Custom prompt engineering for medical contexts

### Backend
- Python 3.9+
- Flask web framework
- SQLite database
- Integration with Google Cloud AI services

### Frontend
- HTML5, CSS3, JavaScript
- Responsive design components
- Client-side form validation

### RAG CPG Pipeline (Optional Enhancement)
**Core Technologies:**
- Python
- PyMuPDF (fitz)
- Tesseract OCR (pytesseract)
- spaCy NLP pipelines
- Sentence Transformers
- Vertex AI Vector Search

**Pipeline Stages:**
- Text extraction and cleaning
- Chunking and embedding generation
- Vector storage/retrieval

### Frontend
- HTML5, CSS3, JavaScript
- Responsive design components
- Client-side form validation

## Setup Instructions

### Prerequisites
- Python 3.9 or later
- Google Cloud account with:
  - Speech-to-Text API enabled
  - Vertex AI API enabled
  - Service account credentials

### Installation
1. Clone the repository
2. Create and activate virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   .\venv\Scripts\activate  # Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure environment variables in `.env` file

1. Start backend server:
   ```bash
   python -m backend.app
   ```
2. Access application at:
   ```
   http://localhost:5000/frontend/index.html
   ```

## Usage Workflow

1. **Subjective:** Record or type patient history
2. **Objective:** Enter examination findings
3. **Assessment:** Generate and review AI suggestions
4. **Plan:** Create treatment plan with AI assistance
5. **Summary:** Generate final clinical summary

## Project Structure

```
AIMS-website/
├── backend/           # Core application logic
│   ├── app.py         # Main application entry
│   ├── database.py    # Secure data storage
│   ├── services/      # Integration services
│   ├── routes/        # API endpoints
│   └── rag/           # Optional RAG components
├── frontend/          # Clinical interface
│   ├── components/    # Reusable UI elements
│   ├── *.html         # Clinical workflow pages
│   └── *.css          # Clinical styling
├── rag_cpg_pipeline/  # Supporting RAG processing
└── requirements.txt   # Dependency management
```

## Troubleshooting

### Common Issues
- **Database Errors:** Delete `notes_main.db` to reset
- **API Connection Issues:** Verify service account credentials

## Contributing
We welcome contributions from the medical and technical communities. Please contact the development team for contribution guidelines and code of conduct.

## License
This project is currently under development. Licensing information will be provided upon public release.

## Support
For clinical implementation support or technical issues, please contact the development team.