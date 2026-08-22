# Authentication Flow

1. User authenticates with username and password.
2. The server validates the credentials and issues:

   * short-lived JWT access token
   * long-lived refresh token
3. Only the SHA-256 hash of the refresh token is stored in PostgreSQL.
4. Protected endpoints validate the access token signature and registered claims.
5. When the access token expires, the client sends the refresh token.
6. The server:

   * revokes the previous refresh token
   * issues a new refresh token
   * keeps the same token family
7. Reuse of a revoked refresh token causes the entire token family to be revoked.
8. Logout can revoke the current session or all sessions for the user.

---

# Refresh Token Lifecycle

Refresh tokens are managed as server-side sessions rather than treated as long-lived credentials.

```text
Login
  ↓
Refresh Token Created
  ↓
Stored as SHA-256 Hash
  ↓
Client Uses Refresh Token
  ↓
Old Token Revoked
  ↓
New Token Created
  ↓
Same Token Family
```

If a previously revoked refresh token is reused:

```text
Reused Token
     ↓
Token Family Identified
     ↓
Entire Family Revoked
     ↓
Session Requires Re-authentication
```

This limits the impact of a compromised refresh token and provides server-side session revocation.

---