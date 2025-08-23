# Security: Enforce dedicated secret key for approval tokens

**Priority:** 🔴 Critical  
**Labels:** `security`, `bug`, `critical`

## Description
Currently the email service falls back to Flask's `SECRET_KEY` if `APPROVAL_TOKEN_SECRET` is not configured. This creates a security risk by reusing the session key for email tokens.

## Current problematic code (line 23)
```python
secret_key = config.APPROVAL_TOKEN_SECRET or current_app.config['SECRET_KEY']
```

## Security Impact
- Key reuse across different security contexts
- Potential token compromise if session key is exposed
- Violation of security principle of key separation

## Acceptance Criteria
- [ ] Remove fallback to `SECRET_KEY`
- [ ] Raise `ValueError` if `APPROVAL_TOKEN_SECRET` is not configured
- [ ] Add minimum entropy validation for the secret key
- [ ] Update documentation for required environment variable

## Proposed Solution
```python
def _get_serializer(self):
    """Get URL serializer for secure tokens"""
    from app.config import config
    
    if not config.APPROVAL_TOKEN_SECRET:
        raise ValueError("APPROVAL_TOKEN_SECRET must be configured for email service")
    
    # Validate minimum entropy (at least 32 characters)
    if len(config.APPROVAL_TOKEN_SECRET) < 32:
        raise ValueError("APPROVAL_TOKEN_SECRET must be at least 32 characters long")
    
    return URLSafeTimedSerializer(config.APPROVAL_TOKEN_SECRET)
```