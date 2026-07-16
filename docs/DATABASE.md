# MedEase AI - Database Documentation

## Overview

PostgreSQL database with 16 tables supporting the full MedEase AI platform.

## Tables

| Table | Description | Phase |
|-------|-------------|-------|
| `users` | User accounts and profiles | ✅ |
| `subjects` | Academic subjects | ✅ |
| `notes` | Student study notes | ✅ |
| `uploaded_files` | PDF and file uploads | ✅ |
| `flashcards` | Study flashcards | ✅ |
| `quizzes` | Generated quizzes | ✅ |
| `quiz_questions` | Individual quiz questions | ✅ |
| `quiz_results` | Quiz attempt results | ✅ |
| `attendance` | Class attendance records | ✅ |
| `exams` | Scheduled examinations | ✅ |
| `study_plans` | AI-generated study schedules | ✅ |
| `posts` | Community posts | ✅ |
| `comments` | Post comments | ✅ |
| `clinical_cases` | Clinical case scenarios | ✅ |
| `clinical_attempts` | Student case attempts | ✅ |
| `analytics` | Usage analytics events | ✅ |

## Entity Relationships

```
users ──┬── notes
        ├── uploaded_files
        ├── flashcards
        ├── quizzes ── quiz_questions
        │           └── quiz_results
        ├── attendance
        ├── exams
        ├── study_plans
        ├── posts ── comments
        ├── clinical_attempts
        └── analytics

subjects ──┬── notes
           ├── flashcards
           ├── quizzes
           └── attendance

clinical_cases ── clinical_attempts
```

## Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

## Seeding

```bash
# Apply migrations
alembic upgrade head

# Seed development data
python -m app.db.seed
```

Seed data includes:
- Default subjects (Anatomy, Physiology, Biochemistry, etc.)
- Sample clinical cases
- Demo user account (development only)

## Indexes

Key indexes will be created in Phase 2:
- `users.email` (unique)
- `notes.user_id, subject_id`
- `attendance.user_id, date`
- `posts.created_at`
- `analytics.user_id, event_type`

## Connection Strings

```env
# Async (application)
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/medease_ai

# Sync (Alembic migrations)
DATABASE_URL_SYNC=postgresql://user:pass@host:5432/medease_ai
```

## Neon PostgreSQL

For cloud deployment, use Neon's connection pooling:

```env
DATABASE_URL=postgresql+asyncpg://user:pass@ep-xxx.region.aws.neon.tech/medease_ai?sslmode=require
```
