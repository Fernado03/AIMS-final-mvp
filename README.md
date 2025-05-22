# AIMS Medical Scribe

## Description

AIMS (AI Medical Scribe) is a clinical documentation assistant that helps healthcare professionals generate structured SOAP (Subjective, Objective, Assessment, Plan) notes. The application combines voice transcription with AI-assisted content generation to streamline clinical documentation.

## Features

### Core Functionality
- **Voice Transcription:** Capture patient narratives through audio recording
- **SOAP Note Structure:** Organized workflow for each note section
- **AI-Assisted Generation:** Context-aware suggestions for Assessment and Plan sections
- **Clinical Summary:** Automated generation of concise patient summaries

### Technical Features
- **Web-Based Interface:** Responsive design for desktop use
- **Data Persistence:** Patient notes stored securely in local database
- **Real-Time Processing:** Immediate feedback during note creation

## Technology Stack

### Backend
- Python 3.9+
- Flask web framework
- SQLite database
- Google Cloud Speech-to-Text API
- Google Vertex AI (Gemini model)

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
├── backend/           # Flask application
│   ├── app.py         # Main application
│   ├── database.py    # Database operations
│   ├── services/      # Integration services
│   └── routes/        # API endpoints
├── frontend/          # Web interface
│   ├── *.html         # Page templates  
│   ├── *.css          # Stylesheets
│   └── components/    # UI components
├── requirements.txt   # Python dependencies
└── README.md          # This file
```

## Troubleshooting

### Common Issues
- **Database Errors:** Delete `notes_main.db` to reset
- **API Connection Issues:** Verify service account credentials
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

## Contributing
We welcome contributions from the medical and technical communities. Please contact the development team for contribution guidelines and code of conduct.

## License
This project is currently under development. Licensing information will be provided upon public release.

## Support
For clinical implementation support or technical issues, please contact the development team.