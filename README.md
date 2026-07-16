# MedEase AI

> One platform for every medical student's journey.

AI-powered educational platform for MBBS, BDS, Nursing, Pharmacy, Physiotherapy, BAMS, and BHMS students.

## Tech Stack

| Layer | Technologies |
|-------|-------------|
| Frontend | React, TypeScript, Tailwind CSS, React Router, React Query, Axios, Zustand |
| Backend | FastAPI, SQLAlchemy, Alembic, Pydantic, JWT |
| Database | PostgreSQL (Neon) |
| AI | Google Gemini, LangChain, ChromaDB, Sentence Transformers |
| Storage | Cloudinary |
| Deployment | Vercel, Render, Neon PostgreSQL |
| Containerization | Docker, Docker Compose |

## Project Structure

```
medease-ai/
├── backend/          # FastAPI backend (Clean Architecture)
│   ├── app/
│   │   ├── api/      # Routes & dependencies
│   │   ├── core/     # Config, security, exceptions
│   │   ├── db/       # Database session & base
│   │   ├── models/   # SQLAlchemy ORM models
│   │   ├── schemas/  # Pydantic request/response schemas
│   │   ├── repositories/  # Data access layer
│   │   └── services/ # Business logic layer
│   ├── alembic/      # Database migrations
│   └── tests/        # Backend tests
├── frontend/         # React frontend (Feature-based)
│   └── src/
│       ├── features/ # Feature modules
│       ├── components/
│       ├── layouts/
│       ├── hooks/
│       ├── lib/
│       ├── store/
│       └── routes/
└── docs/             # Documentation
```

## Quick Start

### Prerequisites

- Node.js 20+
- Python 3.11+
- PostgreSQL 15+

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements-dev.txt
cp .env.example .env
uvicorn app.main:app --reload
```

API docs: http://localhost:8000/docs

### Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

App: http://localhost:5173

## Development Phases

| Phase | Status | Description |
|-------|--------|-------------|
| 1 | ✅ Complete | Project setup + folder structure |
| 2 | ✅ Complete | Database + models |
| 3 | ✅ Complete | Authentication |
| 4 | ✅ Complete | Frontend layout |
| 5 | 🔜 Next | Notes |
| 6 | Pending | PDF Chat RAG |
| 7 | Pending | AI Tutor |
| 8 | Pending | Quiz + Flashcards |
| 9 | Pending | Attendance + Study Planner |
| 10 | Pending | Community |
| 11 | Pending | Clinical Cases |
| 12 | Pending | Analytics |
| 13 | Pending | Testing |
| 14 | Pending | Docker |
| 15 | Pending | Deployment |

## License

Proprietary - All rights reserved.
