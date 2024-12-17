# Ecommerce-Django-REST-APIs (RadinGalleryAPI)

## Overview
RadinGalleryAPI is a project built with Django REST Framework designed to provide a complete set of APIs for an e-commerce site. This includes features like user authentication, product management, and more. The goal is to develop, test, and document these APIs thoroughly, ensuring seamless integration and a high-quality experience.

## API Documentation
You can view the latest API documentation, including the current status of all endpoints, through the Swagger interface at the following link:  
[Swagger Documentation](https://mhdemd.github.io/Ecommerce-Django-REST-APIs/)

## Features
- Full API implementation for an e-commerce site using Django REST Framework.
- User authentication and authorization.
- Integration with Swagger for easy documentation and seamless API interaction.
- Dockerized application setup with Django and PostgreSQL for the database.
- Use of Redis for:
  - Caching data, including storing user click counts for throttling purposes.
  - Storing Django's default session data.
  - Managing task queues as a message broker for Celery.
  - **Storing temporary tokens** for email verification and OTPs for enhanced security and performance.
  ![Demo](assets/pytest.gif)


## Security Measures
This repository incorporates multiple layers of security to protect the application and its users against common vulnerabilities and attacks. Below are the key measures:

### 1. **Authentication and Authorization**
- JWT-based authentication using `rest_framework_simplejwt` ensures secure user sessions.
- `ROTATE_REFRESH_TOKENS` and `BLACKLIST_AFTER_ROTATION` prevent **Replay Attacks**.

### 2. **Rate Limiting**
- Configured rate limiting for both authenticated and anonymous users to mitigate **Brute Force Attacks** and **Denial of Service (DoS)**.

### 3. **Password Security**
- Strong password validation with Django's `AUTH_PASSWORD_VALIDATORS` to enforce:
  - Minimum length of 9 characters.
  - Prevention of common and fully numeric passwords.
- Secure password storage with hashing via Django's `AUTH_USER_MODEL`.

### 4. **Two-Factor Authentication (2FA)**
- OTP-based 2FA implemented to enhance login security using email or SMS.

### 5. **Session Management**
- Sessions are managed and stored securely in Redis, providing protection against **Session Hijacking**.
- Features to list and terminate active sessions for enhanced control.

### 6. **Email Verification**
- Temporary tokens with a 1-hour expiration for email verification and password reset, reducing the risk of **Token Replay** and **Phishing**.

### 7. **Input Validation**
- Comprehensive input validation using DRF serializers to prevent **SQL Injection** and **XSS (Cross-Site Scripting)**.

### 8. **Redis for Temporary Data**
- Secure storage of temporary tokens and OTPs in Redis with short TTLs to minimize exposure.

### 9. **Throttling**
- User and anonymous throttling configured to limit abusive or excessive API requests.

### 10. **Database Security**
- PostgreSQL is used for its robust security features, reducing vulnerabilities associated with other database systems.

### 11. **Logging**
- Centralized logging of critical operations, including login attempts, password changes, and session management, for auditing and monitoring purposes.

## License
This project is licensed under the [MIT License](./LICENSE.md). By using this software, you agree to the terms and conditions outlined in the License.

## Contribute
We welcome contributors to help enhance this project! Whether you have ideas for new features, bug fixes, or improvements, your help would be greatly appreciated.

To contribute:
1. Fork the repository.
2. Clone your fork to your local machine.
3. Create a new branch for your changes.
4. Make your modifications and commit them.
5. Push your branch to your fork.
6. Create a pull request.

Feel free to reach out or open an issue for discussions and suggestions.

## Contact
If you have any questions, please contact me at [mahdi.emadi@yahoo.com](mailto:mahdi.emadi@yahoo.com).
