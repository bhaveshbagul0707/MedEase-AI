# MedEase AI - API Documentation

Base URL: `http://localhost:8000/api/v1`

## Response Format

All API responses follow this structure:

```json
{
  "success": true,
  "message": "Description of the result",
  "data": {}
}
```

Error responses:

```json
{
  "success": false,
  "message": "Error description",
  "data": null
}
```

## Authentication

Protected endpoints require a Bearer token:

```
Authorization: Bearer <access_token>
```

## Endpoints

### Health Check

```
GET /health
```

Response:
```json
{
  "success": true,
  "message": "MedEase AI is running",
  "data": {
    "status": "healthy",
    "version": "0.1.0",
    "environment": "development"
  }
}
```

### Authentication (Phase 3) ✅

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | Login with email/password |
| POST | `/auth/logout` | Logout user (Bearer token required) |
| POST | `/auth/refresh` | Refresh access token |
| GET | `/auth/me` | Get current user profile |
| GET | `/auth/google` | Google OAuth redirect |
| GET | `/auth/google/callback` | Google OAuth callback |
| POST | `/auth/forgot-password` | Request password reset |
| POST | `/auth/reset-password` | Reset password with token |

### Notes (Phase 5)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/notes` | List notes (paginated) |
| POST | `/notes` | Create note |
| GET | `/notes/{id}` | Get note by ID |
| PUT | `/notes/{id}` | Update note |
| DELETE | `/notes/{id}` | Delete note |

### PDF Chat (Phase 6)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/pdf/upload` | Upload PDF file |
| POST | `/pdf/chat` | Chat with PDF (RAG) |
| GET | `/pdf/conversations` | List conversations |

## Pagination

List endpoints support:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `page` | 1 | Page number |
| `page_size` | 20 | Items per page |
| `sort_by` | created_at | Sort field |
| `sort_order` | desc | asc or desc |

## Rate Limiting

Default: 60 requests per minute per IP.

## Interactive Docs

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
