# MedEase AI - Deployment Guide

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌──────────────┐
│   Vercel    │────▶│   Render    │────▶│ Neon Postgres│
│  (Frontend) │     │  (Backend)  │     │  (Database)  │
└─────────────┘     └─────────────┘     └──────────────┘
                           │
                    ┌──────┴──────┐
                    │ Cloudinary  │
                    │  (Storage)  │
                    └─────────────┘
```

## Frontend (Vercel)

1. Connect GitHub repository to Vercel
2. Set root directory to `frontend`
3. Framework preset: Vite
4. Environment variables:
   - `VITE_API_BASE_URL=https://your-api.onrender.com/api/v1`
5. Deploy

## Backend (Render)

1. Create a new Web Service on Render
2. Connect GitHub repository
3. Root directory: `backend`
4. Build command: `pip install -r requirements.txt`
5. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Environment variables: copy from `backend/.env.example`

## Database (Neon)

1. Create a project on [Neon](https://neon.tech)
2. Copy the connection string
3. Set `DATABASE_URL` and `DATABASE_URL_SYNC` in Render env vars
4. Run migrations: `alembic upgrade head`

## Docker (Phase 14)

```bash
docker-compose up -d
```

## CI/CD

GitHub Actions workflow runs on every push:
- Backend: lint, type check, tests
- Frontend: lint, build, tests

## Production Checklist

- [ ] Set strong `SECRET_KEY`
- [ ] Set `APP_ENV=production`
- [ ] Set `DEBUG=false`
- [ ] Configure CORS origins
- [ ] Set up SSL/TLS
- [ ] Configure rate limiting
- [ ] Set up monitoring and logging
- [ ] Run database migrations
- [ ] Configure Cloudinary for file storage
- [ ] Set Gemini API key
