---
name: better-auth-integration
description: Implement authentication using Better Auth (Next.js) and JWT Verification (FastAPI). Use when setting up login, signup, middleware, or protected routes.
allowed-tools: Read, Write, Bash
---

# Better Auth Integration Skill

## Context (The Challenge)
Better Auth runs on the Next.js Frontend (JavaScript), but our Backend is FastAPI (Python). We must use **JWT Tokens** to bridge them[cite: 141, 144].

## 🚨 Critical Rules (Dos and Don'ts)

### 1. Architecture Flow
* **DO** handle Signup/Login/Logout entirely on the **Next.js Frontend** using Better Auth[cite: 150].
* **DON'T** implement `login` or `register` logic inside FastAPI. FastAPI should ONLY verify tokens[cite: 160].
* **DO** configure Better Auth to issue **JWT Tokens** via the JWT plugin[cite: 155].

### 2. The Shared Secret
* **CRITICAL:** Both Next.js (`BETTER_AUTH_SECRET`) and FastAPI (`JWT_SECRET`) must share the **EXACT SAME** secret string in their `.env` files[cite: 157].
* If keys don't match, signature verification will fail.

### 3. Frontend Implementation (Next.js)
* **DO** use the Better Auth Client to get the session/token.
* **DO** attach the token to every Backend API request header:
    `Authorization: Bearer <token>`[cite: 150].

### 4. Backend Implementation (FastAPI)
* **DO** implement a Middleware (or Dependency) that:
    1.  Intercepts the `Authorization` header.
    2.  Verifies the JWT signature using the Shared Secret[cite: 151].
    3.  Decodes the `user_id` from the token[cite: 152].
* **DO** return `401 Unauthorized` if the token is missing or invalid[cite: 163].
* **DO** enforce `user_id` filtering on ALL Database queries (User Isolation)[cite: 153].

## Implementation Checklist

- [ ] **Next.js:** Install `better-auth` and enable JWT plugin.
- [ ] **Env:** Set `BETTER_AUTH_SECRET` in both projects.
- [ ] **FastAPI:** Create `get_current_user` dependency that decodes JWT.
- [ ] **DB:** Ensure `Task` table has `user_id` field[cite: 443].

## Example: FastAPI Dependency
```python
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub") # or "id" depending on Better Auth config
        if user_id is None:
            raise credentials_exception
        return user_id
    except JWTError:
        raise credentials_exception