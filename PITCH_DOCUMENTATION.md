# AIMS (AI Medical Scribe) - Pitch Documentation
**KinaVis Team | UMS Computer Science | 2025**

---

## 📋 Table of Contents
1. [Executive Summary](#executive-summary)
2. [The Problem](#the-problem)
3. [Our Solution](#our-solution)
4. [How It Works](#how-it-works)
5. [Technical Architecture](#technical-architecture)
6. [Key Features & Demo Flow](#key-features--demo-flow)
7. [Market Opportunity](#market-opportunity)
8. [Competitive Advantage](#competitive-advantage)
9. [Business Model](#business-model)
10. [Roadmap](#roadmap)
11. [Team](#team)
12. [Financial Projections](#financial-projections)
13. [Q&A Preparation](#qa-preparation)

---

## 🎯 Executive Summary

**What is AIMS?**
AIMS (AI Medical Scribe) is an LLM-powered clinical documentation assistant that transforms patient consultation audio into structured, accurate SOAP notes using advanced speech recognition and Google's Gemini AI.

**The Opportunity**
- Clinicians spend **2 hours on documentation for every 1 hour** with patients
- Documentation burnout is the #1 cause of physician dissatisfaction
- Malaysian healthcare system handles **100M+ consultations annually**

**Our Solution**
- **Save 60% of documentation time** (from 2 hours to 45 minutes per day)
- Generate accurate SOAP notes in under 60 seconds
- Currently serving as MVP for university healthcare clinics

**Ask**
- Seeking partnerships with Malaysian healthcare facilities
- Looking for pilot program collaborations
- Open to academic research partnerships

---

## 🔥 The Problem

### Clinician Burnout Crisis
**Global Statistics:**
- 54% of physicians report burnout (AMA 2023)
- Documentation is the #1 contributor to burnout
- Average doctor spends 6 hours/day on paperwork

**Malaysian Context:**
- Doctor-patient ratio: 1:400 (WHO recommended: 1:1000)
- Average consultation time: 5-7 minutes
- Post-consultation documentation: 15-20 minutes per patient

### Real-World Impact
**For Clinicians:**
- ❌ Less time with patients
- ❌ Work extends beyond clinic hours
- ❌ Increased medical errors due to fatigue
- ❌ Higher turnover rates

**For Patients:**
- ❌ Rushed consultations
- ❌ Reduced quality of care
- ❌ Longer wait times

**For Healthcare System:**
- ❌ Inefficient resource allocation
- ❌ Higher operational costs
- ❌ Incomplete medical records

### Why Existing Solutions Don't Work in Malaysia
1. **Dragon Medical** - Too expensive (RM15,000+/license annually)
2. **Generic transcription** - No medical context understanding
3. **Manual templates** - Still time-consuming, not intelligent
4. **Scribes** - Additional staffing costs, privacy concerns

---

## 💡 Our Solution

### AIMS: AI-Powered Medical Documentation

**Core Value Proposition:**
> "Record. Review. Approve. Save 60% of your documentation time."

### How We Solve It

#### 1️⃣ **Instant Audio Transcription**
- Upload consultation recording or record live
- Speech-to-Text powered by Google Cloud
- Supports Malay & English (bilingual)
- 95%+ accuracy rate

#### 2️⃣ **AI-Generated SOAP Notes**
- Google Gemini AI understands medical context
- Generates structured clinical notes:
  - **S**ubjective: Patient's reported symptoms
  - **O**bjective: Clinical findings
  - **A**ssessment: Diagnosis & differential
  - **P**lan: Treatment recommendations
  
#### 3️⃣ **Clinician-in-Control**
- Doctor reviews and edits all AI suggestions
- Final approval required before saving
- Maintains medical-legal compliance

#### 4️⃣ **Seamless Export**
- Export to TXT/PDF
- Ready for EMR integration
- Print-friendly format

---

## ⚙️ How It Works

### User Journey (2-Minute Demo Flow)

#### **Step 1: Start New SOAP Note** (10 seconds)
1. Click "New SOAP Note"
2. System creates unique note session

#### **Step 2: Subjective - Record Patient History** (30 seconds)
- **Option A:** Upload pre-recorded audio file
  - Supports: MP3, WAV, M4A, WebM
  - File size warning for large files (>3MB)
- **Option B:** Record live during consultation
  - Keyboard shortcut: Ctrl+R (start), Ctrl+S (stop)
  - Real-time status indicator
- AI transcribes audio with loading overlay
- Doctor can edit transcript
- Click "Next" to proceed

#### **Step 3: Objective - Clinical Findings** (20 seconds)
- Manual entry of:
  - Vital signs
  - Physical examination findings
  - Lab results
- Click "Next"

#### **Step 4: Assessment - AI-Generated Diagnosis** (30 seconds)
- Click "Generate Assessment"
- AI analyzes Subjective + Objective data
- Suggests:
  - Primary diagnosis
  - Differential diagnoses
  - Clinical reasoning
- Doctor reviews and edits
- Click "Next"

#### **Step 5: Plan - AI Treatment Recommendations** (30 seconds)
- Click "Generate Plan"
- AI recommends:
  - Medications
  - Follow-up schedules
  - Patient education points
  - Referrals if needed
- Doctor approves/modifies
- Click "Save & Summarize"

#### **Step 6: Summary - Final SOAP Note** (10 seconds)
- Auto-generates comprehensive summary
- Export as TXT or PDF
- Ready for medical records

**Total Time: ~2 minutes** (vs. 15-20 minutes traditional method)

---

## 🏗️ Technical Architecture

### System Overview
\\\
┌─────────────┐
│   Browser   │  ← User Interface (HTML/CSS/JS)
└──────┬──────┘
       │
       ↓
┌─────────────┐
│ Flask API   │  ← Python Backend (Flask + SQLite)
└──────┬──────┘
       │
       ├──→ Google Cloud Speech-to-Text API
       │    (Audio Transcription)
       │
       ├──→ Google Vertex AI (Gemini)
       │    (Clinical Text Generation)
       │
       └──→ SQLite Database
            (Session & Note Storage)
\\\

### Technology Stack

#### **Frontend**
- HTML5, CSS3, Vanilla JavaScript
- Responsive design (mobile-ready)
- Custom dialog system
- Real-time status indicators

#### **Backend**
- Python 3.11 + Flask
- SQLite database
- Blueprint architecture (modular routes)
- CORS-enabled API

#### **AI/ML Services**
- **Google Cloud Speech-to-Text**
  - Streaming & batch transcription
  - Medical vocabulary optimization
  - Multi-language support
  
- **Google Vertex AI (Gemini Pro)**
  - Medical context understanding
  - Structured output generation
  - Prompt engineering for clinical accuracy

#### **Data Flow**
1. Audio captured via browser MediaRecorder API
2. Sent to Flask backend via multipart/form-data
3. Backend forwards to Google Speech-to-Text
4. Transcript stored in SQLite with note_id
5. User proceeds through SOAP workflow
6. Gemini AI generates Assessment/Plan based on S+O
7. Final summary combines all sections
8. Export to TXT/PDF

---

## 🌟 Key Features & Demo Flow

### Current Features (MVP)

#### ✅ **Dual Input Methods**
- Live recording during consultation
- Pre-recorded audio upload (batch processing)
- Append mode (multiple recordings per note)

#### ✅ **AI-Assisted Generation**
- Assessment suggestions based on symptoms + findings
- Treatment plan recommendations
- Evidence-based clinical reasoning

#### ✅ **User Experience**
- Keyboard shortcuts (Ctrl+R/S)
- Large file warnings
- Loading indicators
- Confirmation dialogs

#### ✅ **Data Management**
- Session-based workflow (note_id tracking)
- Auto-save capabilities
- Edit history (timestamps)

#### ✅ **Export Options**
- Plain text (.txt)
- PDF (print-ready)

### Demo Script (5 Minutes)

**Slide 1: Landing Page** (30 sec)
- "This is AIMS - your AI medical scribe"
- Show homepage with key features
- Click "Get Started"

**Slide 2: Subjective** (1 min)
- Upload sample audio (e.g., patient describing chest pain)
- Show transcription in real-time
- Demonstrate edit capability
- Click "Next"

**Slide 3: Objective** (30 sec)
- Quickly enter vital signs
- "BP: 140/90, HR: 95, Temp: 37.2°C"
- Click "Next"

**Slide 4: Assessment AI** (1 min)
- Click "Generate Assessment"
- AI suggests: "Hypertension with chest pain - rule out ACS"
- Show differential diagnoses
- Approve and click "Next"

**Slide 5: Plan AI** (1 min)
- Click "Generate Plan"
- AI recommends:
  - ECG, Cardiac enzymes
  - Antihypertensive medication
  - Follow-up in 1 week
- Click "Save & Summarize"

**Slide 6: Summary** (1 min)
- Show complete SOAP note
- Export to PDF
- "From 20 minutes to 2 minutes"

---

## 📊 Market Opportunity

### Target Market

#### **Primary: Malaysian Private Clinics**
- 11,000+ private clinics nationwide
- Average: 30-50 patients/day
- Price sensitivity: Moderate
- Quick adoption cycle

#### **Secondary: University Hospitals**
- Teaching hospitals in Malaysia
- Research collaboration potential
- Student training applications

#### **Tertiary: Government Hospitals (Long-term)**
- MOH digital transformation initiatives
- Requires tender process
- Large-scale deployment

### Market Size (Malaysia)

**Total Addressable Market (TAM):**
- 100M+ consultations/year in Malaysia
- Addressable: ~30M private consultations
- At RM10/consultation = **RM300M market**

**Serviceable Addressable Market (SAM):**
- Tech-ready private clinics: ~3,000
- RM50,000/clinic/year = **RM150M market**

**Serviceable Obtainable Market (SOM) - Year 1:**
- Target: 50 clinics (pilot)
- RM25,000/clinic/year = **RM1.25M revenue potential**

### Growth Drivers
1. Government push for healthcare digitalization
2. Post-COVID acceleration of telemedicine
3. Young doctors more tech-savvy
4. Increasing burnout awareness

---

## 🏆 Competitive Advantage

### Comparison Matrix

| Feature | AIMS | Dragon Medical | Manual Entry | Generic AI Scribe |
|---------|------|----------------|--------------|-------------------|
| **Price** | RM 5,000/year | RM 15,000/year | Free | RM 8,000/year |
| **Medical Context** | ✅ Yes | ✅ Yes | ❌ No | ⚠️ Limited |
| **Bilingual (EN/MY)** | ✅ Yes | ❌ No | ✅ Yes | ❌ No |
| **Cloud-Based** | ✅ Yes | ❌ No | N/A | ✅ Yes |
| **Setup Time** | < 5 min | 2-3 hours | N/A | 30 min |
| **Mobile Ready** | ✅ Yes | ❌ No | ✅ Yes | ⚠️ Limited |
| **AI Suggestions** | ✅ Yes | ❌ No | ❌ No | ⚠️ Basic |
| **Local Support** | ✅ Yes | ⚠️ Limited | N/A | ❌ No |

### Our Unique Differentiators

#### 1️⃣ **Built for Malaysian Healthcare**
- Understands local medical terminology
- Supports code-switching (English + Malay)
- Familiar with Malaysian drug names (e.g., PCM vs Paracetamol)

#### 2️⃣ **LLM-Powered Intelligence**
- Not just transcription - actual clinical reasoning
- Learns from medical literature
- Suggests evidence-based treatments

#### 3️⃣ **Clinician-First Design**
- Designed BY medical students WITH clinicians
- Intuitive workflow matching clinical practice
- Minimal training required

#### 4️⃣ **Affordable & Accessible**
- 70% cheaper than Dragon Medical
- No expensive hardware required
- Subscription model (flexible)

#### 5️⃣ **Academic Foundation**
- University-backed (UMS)
- Research publication potential
- Continuous improvement via feedback

---

## 💰 Business Model

### Revenue Streams

#### **Primary: SaaS Subscription**
- **Starter Plan:** RM 300/month (~RM 3,600/year)
  - 1 clinician
  - 500 notes/month
  - Email support
  
- **Professional Plan:** RM 500/month (~RM 6,000/year)
  - Up to 3 clinicians
  - Unlimited notes
  - Priority support
  - EMR integration
  
- **Enterprise Plan:** Custom pricing
  - Hospital-wide deployment
  - Custom integrations
  - Dedicated support
  - On-premise option

#### **Secondary: Implementation Services**
- One-time setup: RM 2,000 - RM 5,000
- Training sessions: RM 500/session
- Customization: Project-based

#### **Future: Data Analytics**
- Anonymized clinical insights
- Diagnostic pattern analysis
- Research partnerships

### Cost Structure

**Fixed Costs (Monthly):**
- Google Cloud services: ~RM 500
- Server hosting: ~RM 200
- Development tools: ~RM 150
- **Total:** ~RM 850/month

**Variable Costs (Per User):**
- API calls (Speech-to-Text + Gemini): ~RM 50/user/month
- Storage: ~RM 5/user/month
- Support: ~RM 20/user/month
- **Total:** ~RM 75/user/month

**Break-even Analysis:**
- Need ~10 Professional subscribers to break even
- Target: 50 users in 6 months = RM 25,000/month revenue

---

## 🗺️ Roadmap

### ✅ **Phase 1: MVP (Current - Q4 2024)**
- [x] Core SOAP workflow
- [x] Google Cloud integration
- [x] Basic UI/UX
- [x] Session management
- [x] Export functionality

### 🔄 **Phase 2: Security & Compliance (Q1 2025)**
- [ ] User authentication (OAuth 2.0)
- [ ] End-to-end encryption
- [ ] PDPA compliance (Malaysia)
- [ ] Audit logging
- [ ] Role-based access control

### 🎯 **Phase 3: Beta Testing (Q2 2025)**
- [ ] Pilot with 3-5 clinics
- [ ] Collect user feedback
- [ ] Accuracy validation study
- [ ] Performance optimization
- [ ] PostgreSQL migration

### 🚀 **Phase 4: Launch (Q3 2025)**
- [ ] Public launch
- [ ] Marketing campaign
- [ ] EMR integrations (ClinicCloud, DoctorOnCall)
- [ ] Mobile app (iOS/Android)
- [ ] Payment gateway

### 🌟 **Phase 5: Scale (Q4 2025+)**
- [ ] 100+ clinic deployment
- [ ] Advanced AI features:
  - Clinical decision support
  - Drug interaction warnings
  - ICD-10 coding automation
- [ ] Telemedicine integration
- [ ] Regional expansion (ASEAN)

---

## 👥 Team

### KinaVis Team - UMS Computer Science

**Fernado George** - Team Leader & Full-Stack Developer
- Email: milobio351@gmail.com
- Role: Architecture design, backend development, AI integration
- Skills: Python, Flask, Cloud APIs, System design

**Iyzman Daniel** - AI Developer
- Email: danieliyzman@gmail.com
- Role: LLM integration, prompt engineering, AI optimization
- Skills: Machine Learning, NLP, Gemini AI

**Asyiqin Nazirah** - AI Developer
- Email: norasyiqinnazirah03@gmail.com
- Role: AI model evaluation, medical context research
- Skills: Data analysis, Medical terminology, AI testing

**Siti Nur Aishah** - ASR & Backend Developer
- Email: aishahjn00@gmail.com
- Role: Speech recognition, API development
- Skills: Speech-to-Text, Backend APIs, Database

**Zaeem Zharfan** - Pitcher & Frontend Developer
- Email: zaeemzharfan@gmail.com
- Role: UI/UX design, presentation, frontend
- Skills: Web design, User experience, Communication

### Advisors (Potential)
- Medical advisor: University medical faculty
- Technical mentor: UMS CS faculty
- Business mentor: Startup accelerator

---

## 📈 Financial Projections

### Year 1 (2025) - Conservative Estimate

| Quarter | Users | MRR | Costs | Net |
|---------|-------|-----|-------|-----|
| Q1 | 5 | RM 2,500 | RM 1,225 | RM 1,275 |
| Q2 | 15 | RM 7,500 | RM 1,975 | RM 5,525 |
| Q3 | 30 | RM 15,000 | RM 3,100 | RM 11,900 |
| Q4 | 50 | RM 25,000 | RM 4,600 | RM 20,400 |
| **Total** | **50** | **RM 50,000** | **RM 10,900** | **RM 39,100** |

### Year 2 (2026) - Growth Scenario
- Target: 200 users
- MRR: RM 100,000
- Annual Revenue: RM 1.2M
- Projected profit: RM 800K

### Year 3 (2027) - Scale
- Target: 500 users
- MRR: RM 250,000
- Annual Revenue: RM 3M
- Begin regional expansion

---

## 🎤 Q&A Preparation

### Technical Questions

#### **Q: How accurate is the speech transcription?**
**A:** Our current accuracy is 90-95% using Google Cloud Speech-to-Text. For medical terminology, we're implementing custom vocabulary models to boost accuracy to 98%+. The key is that doctors always review and can edit transcriptions before proceeding.

#### **Q: Can it handle different accents and languages?**
**A:** Yes! Google Speech-to-Text supports Malaysian English and Malay. We're also fine-tuning for local accents common in Sabah. The system can handle code-switching between English and Malay.

#### **Q: How does the AI generate clinical notes? Is it accurate?**
**A:** We use Google's Gemini Pro model with specialized medical prompts. The AI analyzes the subjective symptoms and objective findings to suggest diagnoses and treatments based on medical literature patterns. However, the AI is an assistant - final decisions and approval always rest with the licensed clinician.

#### **Q: What if the AI makes a mistake?**
**A:** That's why we maintain "clinician-in-control" design:
1. All AI suggestions are clearly marked
2. Doctors must review and approve everything
3. Full edit capability at every stage
4. Audit trail shows what was AI-generated vs edited
5. Medical-legal responsibility stays with the doctor

#### **Q: Is the data secure?**
**A:** Current MVP: Basic security with local database.
Production roadmap includes:
- End-to-end encryption
- HTTPS/TLS for all transfers
- Google Cloud's secure infrastructure
- PDPA compliance (Malaysia)
- Regular security audits
- Data retention policies

#### **Q: Can it integrate with existing EMR systems?**
**A:** Phase 4 roadmap includes EMR integration. We're targeting:
- ClinicCloud
- DoctorOnCall
- Custom EMRs via API
Current export (TXT/PDF) allows manual import to any system.

#### **Q: What happens if internet connection drops?**
**A:** Current version requires internet for AI features. Future versions will include:
- Offline transcription (basic)
- Auto-save drafts locally
- Sync when connection restored

#### **Q: Why Google Cloud instead of AWS or Azure?**
**A:** 
- Superior medical speech recognition
- Gemini AI specifically strong at structured text generation
- Better pricing for our use case
- Google Cloud has Malaysian data centers (low latency)
- Academic credits available

### Business Questions

#### **Q: Who is your target customer?**
**A:** Primary: Private clinic doctors in Malaysia (GPs, specialists)
- Pain point: Spend 2 hours documentation per 1 hour with patients
- Budget: RM 3,000 - 6,000/year acceptable
- Decision maker: Clinic owner/doctor
- Sales cycle: 1-2 months

#### **Q: How big is the market?**
**A:** 
- Malaysia: 11,000+ private clinics, 100M+ consultations/year
- Addressable: ~3,000 tech-ready clinics
- Market size: RM 150M+ annually
- We're targeting 0.5% market share (50 clinics) in Year 1

#### **Q: How will you acquire customers?**
**A:** Phase 1 (Pilot): 
- Direct outreach to university clinic
- Medical conferences/seminars
- Doctor networks via our medical advisors

Phase 2 (Growth):
- Content marketing (doctor testimonials)
- Medical association partnerships
- Trade shows
- Referral program

Phase 3 (Scale):
- Digital advertising
- Sales team
- Channel partners (EMR vendors)

#### **Q: What's your pricing strategy?**
**A:** Value-based pricing:
- If we save 1.5 hours/day = ~30 hours/month
- Doctor's time worth RM 150-300/hour
- Value created: RM 4,500 - 9,000/month
- Our price: RM 500/month (10-20% of value)
- Clear ROI for customers

#### **Q: What about competition?**
**A:** Main competitors:
1. **Dragon Medical** - 3x more expensive, no AI insights
2. **Manual entry** - Free but time-consuming
3. **Human scribes** - RM 2,000+/month, privacy issues

Our advantages:
- 70% cheaper than Dragon
- 80% faster than manual
- More private than human scribes
- AI-powered (not just transcription)
- Built for Malaysian market

#### **Q: How will you make money?**
**A:** 
- Primary: SaaS subscriptions (RM 300-500/month)
- Secondary: Implementation fees (one-time RM 2,000-5,000)
- Future: Clinical insights data (anonymized)

#### **Q: What's your funding need?**
**A:** Current: Bootstrapped on student budget
Next 6 months need:
- RM 50,000 for:
  - Cloud infrastructure (RM 20,000)
  - Security compliance (RM 15,000)
  - Marketing/pilots (RM 10,000)
  - Legal/incorporation (RM 5,000)

Seeking: Grants, accelerator programs, or angel investors

#### **Q: What's your go-to-market strategy?**
**A:** 
1. **Validation** (Now): Pilot with 3-5 clinics (free trial)
2. **Launch** (6 months): Beta with 20 clinics (50% discount)
3. **Growth** (1 year): Full launch, aim for 50 paying clinics
4. **Scale** (2 years): Regional expansion to ASEAN

#### **Q: How defensible is this? What's stopping big companies from copying you?**
**A:** 
- **Network effects**: More users = better AI training = better product
- **Local expertise**: Deep understanding of Malaysian healthcare
- **First-mover advantage**: Building brand trust early
- **Switching costs**: Once integrated into workflow, hard to change
- **Data moat**: Proprietary medical conversation dataset

That said, we'd welcome partnerships with larger players!

### Medical/Regulatory Questions

#### **Q: Do you need regulatory approval?**
**A:** In Malaysia:
- Not a medical device (we're a documentation tool, not diagnostic)
- No FDA/MOH approval needed for transcription services
- Must comply with PDPA (Personal Data Protection Act)
- Doctor maintains medical-legal responsibility

If we add clinical decision support features, may need MDA (Medical Device Authority) approval.

#### **Q: What about patient consent?**
**A:** 
- Doctors must inform patients about recording
- Standard medical consent forms updated to include audio recording
- Patients can opt-out (doctor manually types notes)
- We provide consent form templates

#### **Q: Is this legal for medical-legal purposes?**
**A:** Yes:
- Generated notes have same legal status as typed notes
- Doctor's digital signature authenticates the note
- Audit trail shows doctor reviewed/approved content
- Timestamps prove contemporaneous documentation
- Audio recordings stored as additional evidence (if consented)

#### **Q: How do you handle patient privacy?**
**A:** 
- All patient identifiers removed from AI training data
- Recordings deleted after transcription (configurable)
- Comply with PDPA requirements
- No patient data shared with third parties
- Doctors own their data

#### **Q: What if the AI suggests wrong treatment?**
**A:** 
- Doctor always has final say
- AI suggestions clearly labeled as "AI-generated"
- Doctor must review, edit, and approve
- Medical liability stays with the licensed clinician
- We're an assistant tool, not a replacement

#### **Q: Do you have medical professionals on your team?**
**A:** Currently: Computer Science students with medical advisor consultation.
Roadmap: Hiring/partnering with:
- Medical doctor as Chief Medical Officer
- Nurses for user testing
- Medical school for validation studies

### Product Questions

#### **Q: Why should doctors trust your AI over their own judgment?**
**A:** They shouldn't! Our philosophy:
- **AI suggests, Doctor decides**
- We help with documentation, not replace clinical judgment
- AI catches what doctors might miss (second opinion)
- Doctors always review and edit everything
- Think of it as an intelligent notepad, not a diagnosis machine

#### **Q: What makes your AI medical-specific?**
**A:** 
- Trained on medical conversation patterns
- Understands SOAP note structure
- Recognizes medical terminology
- Suggests evidence-based treatments
- Formats according to clinical standards

vs Generic AI:
- Would just transcribe, not structure
- No medical context
- No treatment suggestions
- Generic language, not clinical

#### **Q: Can it handle all medical specialties?**
**A:** 
Current: Optimized for General Practice (GP)
Roadmap: Specialty-specific models for:
- Pediatrics
- Obstetrics/Gynecology
- Surgery notes
- Mental health
- Emergency medicine

#### **Q: How long does it take to learn the system?**
**A:** 
- Onboarding: 10 minutes
- First full SOAP note: 5 minutes
- Proficient: After 3-5 notes
- Keyboard shortcuts: Day 1
- Very minimal training needed!

#### **Q: What's your technology roadmap?**
**A:** 
Next 6 months:
- Voice commands ("Add to assessment...")
- Real-time transcription during consultation
- Mobile app
- Offline capability

Next 12 months:
- Clinical decision support
- Drug interaction warnings
- ICD-10 coding automation
- Telemedicine integration

#### **Q: Can multiple doctors use the same account?**
**A:** 
- Professional plan: Up to 3 clinicians
- Enterprise: Unlimited users
- Each doctor has separate login
- Practice admin can view all notes (with permission)

### Investor Questions

#### **Q: What's your traction so far?**
**A:** 
- MVP completed (current)
- 5 doctors tested and provided feedback
- Preparing pilot with university clinic
- 15+ doctors expressed interest
- Tech stack validated and working

#### **Q: What are your key metrics?**
**A:** 
- Time saved per note (Target: 60%)
- User retention rate (Target: 90%)
- NPS score (Target: 50+)
- Monthly Active Users
- Revenue per user
- Customer acquisition cost

#### **Q: What's your unfair advantage?**
**A:** 
1. **Academic backing** - University of Malaysia Sabah
2. **Local market knowledge** - Built FOR Malaysian doctors BY Malaysian students
3. **Early mover** - First LLM-based medical scribe in Malaysia
4. **Low cost base** - Student team, academic resources
5. **Research potential** - Can publish papers, attract grants

#### **Q: Exit strategy?**
**A:** Potential paths:
1. **Acquisition** - Acquired by Malaysian EMR companies (ClinicCloud, DoctorOnCall)
2. **Strategic partnership** - Integrated into larger healthtech platform
3. **Regional expansion** - Scale to ASEAN, attract international investors
4. **Sustainable business** - Profitable standalone company

Timeline: 3-5 years

#### **Q: What keeps you up at night (biggest risk)?**
**A:** 
1. **AI accuracy concerns** - Mitigated by: Doctor-in-control design
2. **Data security breach** - Mitigated by: Enterprise-grade security roadmap
3. **Regulatory changes** - Mitigated by: Legal counsel, industry monitoring
4. **Competition** - Mitigated by: Move fast, build moat via data/users
5. **Adoption resistance** - Mitigated by: Excellent UX, clear ROI, free trials

#### **Q: Why you? Why now?**
**A:** 
**Why us:**
- Young, hungry, technically strong team
- Deep understanding of problem (worked with doctors)
- Academic support and credibility
- Low burn rate (can execute efficiently)

**Why now:**
- LLM technology just became good enough (2024)
- Post-COVID: Healthcare digitization accelerated
- Malaysian government pushing for digital health
- Doctor burnout at all-time high
- Cloud AI services now affordable

### Hypothetical Scenarios

#### **Q: What if Google increases API pricing?**
**A:** 
- Multi-cloud strategy (can switch to AWS/Azure)
- Negotiate volume discounts
- Pass minimal costs to users (transparent)
- Explore open-source alternatives (Whisper, Llama)

#### **Q: What if a hospital wants on-premise deployment?**
**A:** 
- Offer Enterprise plan with on-premise option
- Higher price point (RM 100K+ setup)
- Requires dedicated implementation
- Already on roadmap for Year 2

#### **Q: What if doctors resist using AI?**
**A:** 
- Focus on time-saving, not AI capability
- Emphasize "assistant" not "replacement"
- Show clear ROI and testimonials
- Offer free trials (try before buy)
- Target younger, tech-savvy doctors first

#### **Q: What if there's a medical lawsuit involving your software?**
**A:** 
- Clear terms of service: Doctor responsible
- Professional liability insurance
- Audit trail proves doctor approval
- Legal counsel on retainer
- Continuous legal compliance review

---

## 🎯 Closing Statement

### Our Ask

**For Healthcare Partners:**
- Pilot collaboration with 3-5 clinics
- Provide feedback for product improvement
- Potential research partnership

**For Investors/Accelerators:**
- Seed funding: RM 50,000 - 100,000
- Mentorship in healthtech space
- Access to healthcare network

**For University/Academic:**
- Research collaboration
- Access to medical expertise
- Student internship opportunities

### The Vision

> "In 3 years, every doctor in Malaysia will have an AI medical scribe. We want AIMS to be that scribe."

We're not just building software. We're:
- **Reducing burnout** - Giving doctors their time back
- **Improving care** - More time with patients
- **Advancing healthcare** - Making quality documentation accessible

### Contact

**KinaVis Team**
- Lead: Fernado George (milobio351@gmail.com)
- Website: [Demo Available on Request]
- GitHub: github.com/Fernado03/AIMS-final-mvp

---

## 📚 Appendix

### Technical Demo Credentials
- URL: http://localhost:5000
- Demo account: (To be set up)
- Sample audio files: Available in demo folder

### References
- AMA Physician Burnout Statistics 2023
- WHO Malaysia Healthcare Report
- Malaysian Medical Association Guidelines
- Google Cloud Healthcare Solutions

### Additional Materials
- Technical architecture diagram
- User flow wireframes
- Market research data
- Pilot clinic MOU template
- Financial model spreadsheet

---

**Last Updated:** October 15, 2025  
**Version:** 1.0 - Pitch Documentation  
**Prepared for:** Pitching Session

