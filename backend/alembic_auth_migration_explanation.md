Alembic migration: Add authentication-related schema (explanation)

File: alembic/versions/c1a2b3d4e5f6_add_auth_tables_and_user_columns.py

Overview
--------
This migration is additive and intentionally backward-compatible. It introduces support for:

- Persisting refresh token identifiers (jti) and metadata — enabling secure refresh token rotation and revocation without storing full JWTs.
- An append-only authentication audit log for critical events (REGISTER, LOGIN_SUCCESS, LOGIN_FAILURE, EMAIL_VERIFIED, PASSWORD_RESET, PASSWORD_CHANGED, TOKEN_REFRESH, LOGOUT, LOGOUT_ALL_DEVICES, ACCOUNT_LOCKED).
- User model columns to support email verification and account lockout behavior.

Upgrade steps (what the migration does and why)
---------------------------------------------
1) Add columns to the users table
   - email_verification_token (VARCHAR(255), nullable)
     Purpose: store a one-time token used to verify a newly-registered user's email address.
     Rationale: nullable and optional for existing users; safe additive change.

   - email_verification_expires (TIMESTAMP with timezone, nullable)
     Purpose: expiry timestamp for the verification token.

   - failed_login_attempts (INTEGER, NOT NULL, default 0)
     Purpose: track consecutive failed login attempts for rate-limiting and lockout.
     Rationale: default 0 ensures existing users are unaffected at migration time.

   - locked_until (TIMESTAMP with timezone, nullable)
     Purpose: when present and in the future, the account is temporarily locked due to repeated failures.

   These columns enable the application to implement temporary account lockouts and email verification without changing existing data.

2) Create refresh_tokens table
   Columns:
   - id: PK integer autoincrement
   - jti: VARCHAR(128), unique, indexed, not null
   - user_id: FK users.id (ON DELETE CASCADE), not null
   - created_at, expires_at: timestamps with timezone
   - revoked: boolean, default false
   - last_used_at: timestamp with timezone, nullable
   - ip_address: VARCHAR(45), nullable
   - user_agent: VARCHAR(500), nullable

   Purpose: store only the refresh token identifier (jti) and related metadata rather than the full JWT.
   Why: reduces risk if DB leaks, and supports rotation/revocation by checking jti and revoked flag atomically.

   Indexes: unique index on jti for quick lookup and created_at index for listing sessions.

3) Create auth_audit table
   Columns:
   - id: PK
   - user_id: FK users.id (ON DELETE SET NULL), nullable
   - event_type: VARCHAR(50)
   - ip_address, user_agent: optional metadata
   - metadata: TEXT for structured JSON blobs (optional)
   - created_at: timestamp with timezone, not null

   Purpose: append-only audit log for authentication events to support security monitoring, incident investigation, and compliance.
   Notes: user_id is nullable to allow logging of events that are not associated with a known user (e.g., failed login attempts using non-existent emails).

Downgrade steps (what is reversed and rationale)
-----------------------------------------------
- Drops auth_audit and refresh_tokens tables.
- Removes the four columns added to users.

Caveats and operational notes
----------------------------
- The migration sets a server_default of 0 for failed_login_attempts to keep existing rows valid. After running the migration in production, consider issuing an ALTER to drop the server_default if desired.
- The migration references users.id foreign keys with ON DELETE behaviors to avoid orphaned refresh_tokens and preserve audit entries (SET NULL) when a user is removed.
- Because this migration is additive, it is safe to generate and review without applying to production. Do not apply it until you've backed up your production DB and tested the migration in a staging environment.

Next steps after approval
------------------------
- Review and approve the migration file.
- (Optional) I can generate a second migration that fills or indexes historical data, or remove server defaults after rollout.
- After your approval I can apply the migration to a local test DB for an end-to-end verification run; I will not run it against any production DB unless explicitly authorized.
