# MedEase AI: Beginner Guide

## 1. MedEase AI kya hai?

MedEase AI medical students ke liye study platform hai. Isme user:

- account bana sakta hai aur login kar sakta hai;
- apne PDF notes upload kar sakta hai;
- PDF ke content par questions pooch sakta hai;
- notes bana sakta hai;
- notes se flashcards generate karke revise kar sakta hai;
- flashcards se quiz de sakta hai;
- AI Tutor se apne uploaded study material ke basis par help le sakta hai;
- attendance, study plan, community aur clinical cases use kar sakta hai;
- analytics me apni study progress dekh sakta hai.

## 2. Project ke do main parts

### Frontend

Frontend `frontend` folder me hai. Ye React, TypeScript, Vite aur Tailwind CSS use karta hai. Jo screen browser me dikhti hai, jaise Login, Notes, PDF Chat aur Flashcards, wo frontend se aati hai.

### Backend

Backend `backend` folder me hai. Ye FastAPI aur Python use karta hai. Backend:

- login aur authorization handle karta hai;
- database me users, notes, PDFs aur flashcards save karta hai;
- PDF process karta hai;
- API endpoints provide karta hai;
- AI/RAG services chalata hai.

### Database

Is test copy me local SQLite database use ho raha hai:

```text
backend/medease_local.db
```

Ye production database nahi hai. Is project ko chalane ke liye production credentials ya API keys ki zaroorat nahi hai. Default AI providers mock hain.

## 3. Project ka basic flow

1. User frontend par login karta hai.
2. Frontend backend ke `/api/v1` endpoints ko request bhejta hai.
3. Backend access token verify karta hai.
4. Backend database se data read/write karta hai.
5. PDF upload hone par processing pipeline text extract karke chunks aur embeddings banati hai.
6. PDF Chat aur AI Tutor relevant chunks retrieve karte hain.
7. Notes se flashcards aur flashcards se quiz ban sakta hai.

## 4. Project kaise run karein?

### Terminal 1: Backend

PowerShell me:

```powershell
cd "C:\Users\HP\Desktop\medease-ai - Copy.worktrees\test-copy-isolated-modifications\backend"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Backend check:

- API: http://127.0.0.1:8000
- Swagger docs: http://127.0.0.1:8000/docs

### Terminal 2: Frontend

PowerShell ke doosre window me:

```powershell
cd "C:\Users\HP\Desktop\medease-ai - Copy.worktrees\test-copy-isolated-modifications\frontend"
npm run dev
```

Frontend check:

- http://localhost:5173

### Agar port error aaye

Port already kisi process ne use kiya ho sakta hai. Pehle check karein:

```powershell
Get-NetTCPConnection -LocalPort 8000 -State Listen
```

Existing backend ko band karne ke liye us output ka `OwningProcess` PID use karein:

```powershell
Stop-Process -Id <PID>
```

Phir backend command dobara chalayein.

## 5. Beginner ke liye pehla test

1. http://localhost:5173 open karein.
2. Register page par test account banayein.
3. Login karein.
4. Notes page par title aur content bhar kar note banayein.
5. Note ka ID yaad rakhein.
6. Flashcards page par Note ID enter karke **Generate from note** dabayein.
7. Flashcards review karein.
8. Quiz page par quiz start karein.
9. PDF Chat page par ek PDF upload karein.
10. PDF process hone ke baad us PDF ko select karke question poochein.
11. AI Tutor me uploaded material ke baare me question poochein.
12. Analytics page par progress check karein.

## 6. Important pages

| Page | Kaam |
| --- | --- |
| Dashboard | Overall study summary |
| Notes | Notes create, edit aur delete |
| PDF Chat | PDF upload, download aur PDF questions |
| Flashcards | Cards review aur note se generation |
| Quiz | Flashcards se quiz |
| AI Tutor | Study material based questions |
| Analytics | Flashcards, reviews aur quizzes ki progress |
| Attendance | Attendance records |
| Study Planner | Study plans |
| Community | Posts aur discussions |
| Clinical Cases | Clinical case practice |
| Settings/Profile | User settings aur profile |

## 7. AI Tutor me “I don't know” kyun aata hai?

AI Tutor uploaded aur successfully processed study material se answer banata hai. Agar:

- PDF upload nahi hui;
- PDF processing `FAILED` hai;
- PDF me readable text nahi hai;
- question ke liye matching chunk nahi mila;

to tutor safe response ke roop me `I don't know.` dikha sakta hai. Pehle PDF Library me upload status `PROCESSED` hone ka wait karein.

## 8. Agar Notes ya login error aaye

1. Backend terminal running hai ya nahi check karein.
2. Browser ko refresh karein.
3. Logout karke dobara login karein.
4. Agar backend restart hua hai aur old token error de raha hai, browser local storage clear karke dobara login karein.
5. Swagger par endpoint check karein: http://127.0.0.1:8000/docs

## 9. Current project status

Complete aur connected modules:

- Authentication
- Dashboard
- Notes
- PDF upload/library/download
- PDF processing and RAG foundation
- PDF Chat
- Flashcards and reviews
- Quiz
- AI Tutor
- Analytics
- Attendance
- Study Planner
- Community
- Clinical Cases

Latest verification:

- Backend tests: 29 passed
- Frontend production build: passed
- Note -> Flashcard -> Quiz workflow: passed
- Local SQLite database: working

## 10. Ab tak humne kya banaya hai?

### Authentication

- User registration and login
- Access and refresh tokens
- Refresh-token rotation
- Logout and logout-all-devices
- Active sessions
- Password change support
- Email verification structure
- Failed-login lockout
- Authentication audit logs
- User ownership checks

### PDF Knowledge Pipeline

- PDF upload validation
- Local file storage
- SHA256 duplicate detection
- File size limits
- PDF download
- Soft deletion
- PDF text extraction
- PDF chunking
- Embedding generation
- Vector search foundation
- RAG retrieval
- PDF-specific chat endpoint

### Provider-agnostic AI architecture

AI ko directly ek provider ke saath tightly couple nahi kiya gaya. Interfaces banaye gaye:

- `LLMProvider`
- `EmbeddingProvider`

Available provider structures:

- Mock LLM provider
- OpenAI scaffold
- Gemini scaffold
- Anthropic scaffold
- Mock embedding provider
- OpenAI embedding scaffold
- Gemini embedding scaffold
- Sentence Transformer scaffold

Default provider Mock hai, isliye API key ke bina project local machine par run hota hai.

### Notes

- Notes create, list, update and delete
- User-specific note ownership
- Notes ko PDF/chunk ke saath link karne ki capability
- Notes count query aur frontend redirect issue fix kiya gaya

### Flashcards and Spaced Repetition

- Flashcard CRUD
- Note se flashcard generation
- PDF chunk se flashcard generation
- Flashcard review endpoint
- Correct/incorrect review tracking
- Flashcard schedule
- Review history
- SM-2-style spaced repetition logic
- Frontend par “Generate from note” action

### Quiz

- User flashcards se quiz generation
- Quiz questions retrieval
- Quiz answer submission
- Score calculation
- Quiz result storage

### AI Tutor

- User ke relevant document chunks retrieve karna
- Knowledge-grounded tutor response
- Safe fallback jab matching content available na ho
- Provider abstraction ke saath future AI integration

### Analytics

- Total flashcards
- Learned flashcards
- Due reviews
- Quizzes taken
- Study-progress API
- Frontend analytics cards

### Remaining platform pages

Frontend/backend foundation add kiya gaya:

- Attendance
- Study Planner
- Community
- Clinical Cases
- Profile
- Settings
- Dashboard

In modules ka basic API aur frontend structure available hai; future me inme advanced business workflows add kiye ja sakte hain.

## 11. Humne kya use kiya hai?

### Frontend technologies

- React
- TypeScript
- Vite
- Tailwind CSS
- Axios
- React Router
- Zustand
- Lucide React icons
- Vitest

### Backend technologies

- Python
- FastAPI
- Pydantic v2
- SQLAlchemy async
- Alembic
- SQLite for isolated local development
- PostgreSQL compatibility for future deployment
- Pytest
- Pypdf

### AI and search technologies

- Provider-agnostic LLM interface
- Provider-agnostic embedding interface
- Mock LLM provider
- Mock deterministic embeddings
- Chroma vector-store adapter
- Database-backed vector store for tests/fallback
- RAG retrieval pipeline

### Development tools

- VS Code
- PowerShell
- Git
- npm
- Python virtual environment/dependencies
- Swagger/OpenAPI documentation
- Local browser testing

### Architecture patterns

- Clean Architecture style separation
- API routes
- Schemas
- Services
- Repositories
- Database models
- Provider interfaces
- Dependency injection
- Ownership and authorization checks

## 12. Important files and folders

```text
backend/
  app/
    api/          API routes
    core/         Configuration and security
    models/       Database models
    repositories/ Database access
    schemas/      Request/response validation
    services/     Business logic and AI pipeline
  tests/          Backend tests
  medease_local.db

frontend/
  src/
    features/    Feature pages
    components/  Reusable UI components
    lib/         API client and utilities
    routes/      Application routes
  package.json

PROJECT_BEGINNER_GUIDE.md
```

## 13. Abhi aapko kya karna hai?

### Aaj ke liye

1. Dono terminals me backend aur frontend start karein.
2. Ek fresh test account banayein.
3. Note create karke flashcards generate karein.
4. Quiz submit karein.
5. Ek text-based PDF upload karke processing status check karein.
6. PDF Chat aur AI Tutor verify karein.
7. Agar koi error aaye to screenshot ke saath endpoint aur error message note karein.

### Uske baad

- Real AI provider use karna ho to provider configuration aur API key manually set karni hogi.
- PDF OCR ke liye OCR provider add karna hoga.
- Background job worker aur production deployment setup karna hoga.
- Alembic migrations ko review karke approved environment me apply karna hoga.
- Deprecation warnings ko clean up karna hoga.

## 14. Future plan

Priority order:

1. Real PDF processing status and retry UI
2. Better AI provider implementations
3. OCR for scanned PDFs
4. More accurate RAG citations and sources
5. Full flashcard editing and deletion UI
6. Advanced quiz types and explanations
7. Detailed analytics charts
8. Complete Attendance and Study Planner workflows
9. Community moderation and notifications
10. Clinical case scoring and history
11. Background workers and job queue
12. Production migrations and deployment
13. Docker and CI/CD

## 15. Important safety rule

Ye test copy isolated hai. `backend/.env` me production database, production API key, ya production token kabhi na daalein. Local development ke liye SQLite aur mock providers ka use karein.
