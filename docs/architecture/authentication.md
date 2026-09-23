# Authentication Architecture

## Identity Management

DEFEND-X separates the concept of *Identity* from *Candidate Profile*.

### Initial Enrollment Flow
1. Candidates do NOT sign up themselves in Phase 1 design.
2. They receive a `User ID` (username) and a `Temporary Password`.
3. First login requires an immediate password change.

### Password Security
- Passwords MUST NEVER be stored in plaintext.
- The system must use a modern hashing algorithm. We default to **Argon2id**.
- The `users` table will store only the password hash and necessary metadata (e.g., salt if applicable, hash algorithm version).

### Session & Identity
- UUIDs are used internally as primary keys for database rows.
- The UI uses the `User ID`.
- The backend derives identity exclusively from the secure session token (e.g., HTTP-only cookie JWT or session store) provided by the authentication flow.

### Security Boundaries
- The backend API must NEVER trust a UUID sent by the client for data access control.
- All endpoints must resolve the user's UUID from the validated session token.
- Candidate data isolation is strictly enforced. Candidate A cannot query Candidate B's data under any circumstances.
