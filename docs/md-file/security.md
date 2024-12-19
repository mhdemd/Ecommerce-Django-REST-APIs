# Security Measures

This repository incorporates multiple layers of security to protect the application and its users against common vulnerabilities and attacks. Below are the key measures:

## 1. **Authentication and Authorization**
- **JWT-based authentication**: Utilizes JWT for secure user session management.
- **ROTATE_REFRESH_TOKENS and BLACKLIST_AFTER_ROTATION**: Prevents **Replay Attacks** by rotating and blacklisting refresh tokens.

## 2. **Rate Limiting**
- Configured rate limiting for both authenticated and anonymous users to mitigate **Brute Force Attacks** and **Denial of Service (DoS)**.

## 3. **Password Security**
- **Strong password validation**: Implements Django's `AUTH_PASSWORD_VALIDATORS` to enforce:
  - Minimum length of 9 characters.
  - Prevention of common and fully numeric passwords.
- **Secure password storage**: Uses hashing via Django's `AUTH_USER_MODEL` for password storage.

## 4. **Two-Factor Authentication (2FA)**
- Implements OTP-based 2FA to enhance login security using email or SMS.

## 5. **Session Management**
- **Secure session storage in Redis**: Protects against **Session Hijacking** by managing and storing sessions securely.
- Features to list and terminate active sessions for enhanced control.

## 6. **Email Verification**
- Utilizes temporary tokens with a 1-hour expiration for email verification and password reset, reducing the risk of **Token Replay** and **Phishing**.

## 7. **Input Validation**
- **Comprehensive input validation** using DRF serializers to prevent **SQL Injection** and **XSS (Cross-Site Scripting)**.

## 8. **Redis for Temporary Data**
- **Secure storage of temporary tokens and OTPs in Redis** with short TTLs to minimize data exposure.

## 9. **Throttling**
- **Configured throttling** for both users and anonymous requests to limit abusive or excessive API requests.

## 10. **Database Security**
- Uses **PostgreSQL** for its robust security features, reducing vulnerabilities associated with other database systems.

## 11. **Logging**
- **Centralized logging of critical operations**, including login attempts, password changes, and session management, for auditing and monitoring purposes.
