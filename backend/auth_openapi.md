Authentication API - OpenAPI Documentation

This document summarizes the authentication-related HTTP API surface (OpenAPI-style) implemented under /api/v1/auth.
It includes request/response schemas, error responses, authentication requirements, status codes, and examples.

Base path: /api/v1/auth

Common response structure
-------------------------
Most endpoints return the project's APIResponse envelope:
- 200 OK on success, with JSON: {"message": "...", "data": <payload>}
- Error responses use appropriate HTTP status codes and a JSON error format (see Error Responses below).

Schemas referenced
------------------
- TokenResponse:
  - access_token: string
  - refresh_token: string
  - token_type: "bearer"
  - expires_in: integer seconds until access token expiry
  - user: UserResponse

- UserResponse: representation of the user object (id, email, full_name, program, year_of_study, is_active, is_verified, avatar_url, etc.)

- SessionResponse:
  - jti: string
  - created_at: string (ISO 8601)
  - expires_at: string (ISO 8601)
  - revoked: boolean
  - ip_address: string | null
  - user_agent: string | null
  - device_name: string | null
  - browser: string | null
  - os: string | null
  - current: boolean
  - last_used_at: string | null

- MessageResponse: { message: string }

- ForgotPasswordResponse: { message: string, reset_token: string } — for local/testing only (production should email token)

Authentication and security
---------------------------
- Endpoints that require authentication use a Bearer access token in the Authorization header: "Authorization: Bearer <access_token>".
- Access tokens are stateless JWTs (access token type). Refresh tokens are JWTs containing a jti claim; the server persists only the jti for rotation and revocation.

Error Responses
---------------
Standard error payload (example):
- 401 Unauthorized: {"detail": "Not authenticated"} or {"detail": "Invalid or expired token"}
- 403 Forbidden: {"detail": "Account is deactivated"}
- 404 Not Found: {"detail": "Session not found"}
- 409 Conflict: {"detail": "Email already registered"}
- 400 Bad Request: {"detail": "Validation error details..."}

Endpoints (full details)
------------------------
1) POST /auth/register
- Purpose: Create a new user and return an access + refresh token pair.
- Authentication: public
- Request body (application/json):
  {
    "email": "user@example.com",
    "password": "SecurePass123",
    "confirm_password": "SecurePass123",
    "full_name": "Full Name",
    "program": "MBBS",
    "year_of_study": 1
  }
- Responses:
  - 200 OK: APIResponse<TokenResponse>
  - 409 Conflict: Email already registered
- Example request:
  POST /api/v1/auth/register
  {"email":"student@medease.ai","password":"SecurePass123","confirm_password":"SecurePass123","full_name":"Test Student","program":"MBBS","year_of_study":1}
- Example response (success):
  {
    "message":"Registration successful",
    "data":{
      "access_token":"ey...",
      "refresh_token":"ey...",
      "token_type":"bearer",
      "expires_in":3600,
      "user":{...}
    }
  }

2) POST /auth/login
- Purpose: Authenticate user credentials and return token pair.
- Authentication: public
- Request body:
  {"email":"user@example.com","password":"password"}
- Responses:
  - 200 OK: APIResponse<TokenResponse>
  - 401 Unauthorized: invalid creds / account locked
  - 403 Forbidden: account deactivated
- Rate limiting and lockout:
  - After a configurable number of failed attempts (default 5), account is locked for lockout_minutes (default 15).
- Example request/response similar to register.

3) POST /auth/logout
- Purpose: Revoke a provided refresh token (optional). If no token is provided, returns success for compatibility.
- Authentication: none required (token is provided in body); however revocation is based on the refresh token passed.
- Request body (optional): { "refresh_token": "<refresh_jwt>" }
- Responses:
  - 200 OK: { "message": "Logged out successfully", "data": { "message": "Please discard your tokens on the client." } }
  - 401 Unauthorized: invalid / expired refresh token

4) POST /auth/verify-email
- Purpose: Verify user's email using a one-time verification token.
- Authentication: public for token-based verification (the implementation expects a token in the body). Note: the project also supports an authenticated resend verification endpoint (authenticated only).
- Request body: { "token": "<verification_token>" }
- Responses:
  - 200 OK: { "message": "Email verified", "data": { "message": "Email verified successfully" } }
  - 401 Unauthorized: invalid or expired token

5) GET /auth/sessions
- Purpose: List all refresh-token sessions for the current authenticated user (Active Sessions API).
- Authentication: Requires Authorization: Bearer <access_token>
- Optional query/body: current_refresh_token (string) — if provided, used to mark the current session in the result.
- Responses:
  - 200 OK: APIResponse<array of SessionResponse>
  - 401 Unauthorized: not authenticated
- Example response (success):
  {
    "message":"Active sessions",
    "data":[
      {
        "jti":"abc123",
        "created_at":"2026-08-07T00:00:00Z",
        "expires_at":"2026-08-14T00:00:00Z",
        "revoked":false,
        "ip_address":"203.0.113.5",
        "user_agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
        "device_name":"Desktop",
        "browser":"Chrome",
        "os":"Windows",
        "current":true,
        "last_used_at":"2026-08-07T00:10:00Z"
      }
    ]
  }

6) DELETE /auth/sessions/{jti}
- Purpose: Revoke a single session identified by its jti.
- Authentication: Requires Authorization: Bearer <access_token> (user must own the session)
- Path parameter: jti (string)
- Responses:
  - 200 OK: { "message": "Session revoked", "data": { "message": "Session revoked" } }
  - 404 Not Found: Session not found or does not belong to user
  - 401 Unauthorized: not authenticated

7) POST /auth/sessions/revoke-all
- Purpose: Revoke all sessions for the authenticated user.
- Authentication: Requires Authorization: Bearer <access_token>
- Responses:
  - 200 OK: { "message": "All sessions revoked", "data": { "message": "All sessions revoked" } }

8) POST /auth/refresh
- Purpose: Exchange a refresh token for a new access token pair using rotation.
- Authentication: public; requires refresh token in body
- Request body: { "refresh_token": "<refresh_jwt>" }
- Responses:
  - 200 OK: APIResponse<TokenResponse> (new refresh token created server-side and its jti persisted)
  - 401 Unauthorized: invalid or expired refresh token
  - Note: The server implements rotation and will revoke the presented refresh token atomically and create a new one.

9) GET /auth/me
- Purpose: Get current authenticated user's profile.
- Authentication: Requires Authorization: Bearer <access_token>
- Responses:
  - 200 OK: APIResponse<UserResponse>

10) PATCH /auth/me
- Purpose: Update current user's profile fields
- Authentication: Requires Authorization: Bearer <access_token>
- Request body: partial UserUpdateRequest (e.g., full_name, avatar_url)
- Responses:
  - 200 OK: APIResponse<UserResponse>

11) POST /auth/change-password
- Purpose: Change password for the authenticated user.
- Authentication: Requires Authorization: Bearer <access_token>
- Request body: { "old_password": "...", "password": "...", "confirm_password": "..." }
- Behavior: Revokes all refresh tokens for the user after a successful password change (revoke_all_for_user)
- Responses:
  - 200 OK: MessageResponse
  - 401 Unauthorized: invalid current password

12) POST /auth/forgot-password
- Purpose: Initiate password reset flow; returns a reset token in test environment.
- Authentication: public
- Request body: { "email": "user@example.com" }
- Responses:
  - 200 OK: ForgotPasswordResponse { "message": "...", "reset_token": "<token>" }
  - Note: In production, reset token is normally sent via email; the returned token in response is intended for local testing only.

13) POST /auth/reset-password
- Purpose: Complete password reset using the reset token and set a new password.
- Authentication: public
- Request body: { "token": "<reset_token>", "password": "...", "confirm_password": "..." }
- Responses:
  - 200 OK: APIResponse<TokenResponse> (logs PASSWORD_RESET in audit)

14) Google OAuth endpoints
- GET /auth/google: redirect to provider (requires google_client_id/secret configured).
- GET /auth/google/callback: callback endpoint, accepts provider response and issues TokenResponse. Response is a RedirectResponse to the frontend with access_token & refresh_token as query params.

Examples
--------
Register example (curl):

curl -X POST "http://localhost:8000/api/v1/auth/register" -H "Content-Type: application/json" -d '{"email":"student@medease.ai","password":"SecurePass123","confirm_password":"SecurePass123","full_name":"Test Student","program":"MBBS","year_of_study":1}'

Login example:

curl -X POST "http://localhost:8000/api/v1/auth/login" -H "Content-Type: application/json" -d '{"email":"student@medease.ai","password":"SecurePass123"}'

Refresh example:

curl -X POST "http://localhost:8000/api/v1/auth/refresh" -H "Content-Type: application/json" -d '{"refresh_token":"<refresh_jwt>"}'

Security recommendations (for implementers)
------------------------------------------
- Store refresh tokens in secure, httpOnly cookies for web clients and use SameSite/secure flags.
- Treat any received refresh token rotate/revocation as an authentication-sensitive action; log event to audit.
- Enforce rate-limiting on login and forgot-password endpoints.
- In production, do not return reset or verification tokens in API responses; instead send via email.

Notes about documentation accuracy
---------------------------------
This documentation was generated from the current codebase routes and service behavior. It intentionally omits implementation-level details (e.g., exact claim names and expiry seconds) that are defined in the core security configuration. Use this as a complete human-readable reference for the Authentication API; it can be converted to OpenAPI YAML/JSON if desired.
