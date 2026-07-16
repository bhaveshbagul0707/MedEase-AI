# MedEase AI - Installation Guide

## Prerequisites

- **Node.js** 20 or higher
- **Python** 3.11 or higher
- **PostgreSQL** 15 or higher (or Neon cloud database)
- **Git**

## 1. Clone the Repository

```bash
git clone <repository-url>
cd medease-ai
```

## 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate
# Activate (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements-dev.txt

# Configure environment
cp .env.example .env
# Edit .env with your database URL, secret key, and API keys

# Run migrations (after Phase 2)
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env

# Start development server
npm run dev
```

## 4. Verify Installation

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000/api/v1/health
- API Docs: http://localhost:8000/docs

## Environment Variables

See `backend/.env.example` and `frontend/.env.example` for all required variables.

### Required for Full Functionality

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `SECRET_KEY` | JWT signing key |
| `GEMINI_API_KEY` | Google Gemini API key |
| `CLOUDINARY_*` | Cloudinary storage credentials |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID |
