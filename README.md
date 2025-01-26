**Communication and Authentication System 🔐📱**

> 👨‍💻 **Project Authors**:
> - Backend - Hryshyn Mykyta
> - Frontend - Aleksandr Albekov

> 🎯 A test task for developing a communication and authentication system using Django and Next.js.

> ℹ️ **Project Status**: Completed as a developer-mode test project. All functionality is implemented and working but requires business account verification to use external APIs like Meta/Facebook and WhatsApp in production.

A scalable system for user authentication and multichannel communication built on Django and Next.js. It includes secure authentication mechanisms, social login, and messaging via WhatsApp and email.

---

## 📝 **About the Test Task**

The task involved creating the following key components:
1. WhatsApp API integration (Twilio/Meta Cloud API)
2. Email sending system (Gmail/Office 365)
3. Authentication system with:
   - Token-based logout
   - Facebook social login
   - Country-based IP access restriction

---

## 🤔 **Challenges and Solutions**

### WhatsApp Integration
- Chose Meta Cloud API due to higher limits on the free tier.
- Constraints in developer mode:
  - 5 test numbers limit
  - Custom messages only after user replies to a template.
- Asynchronous message handling using Celery to prevent timeouts.
- Implemented retry mechanisms for API errors.

### Email Integration
- Secure SMTP setup for Gmail/Office 365.
- Queued processing for bulk email campaigns.
- Gmail API limitations addressed with custom error handling.

### Facebook Authentication
- Limited functionality in Meta developer mode (requires app publishing).
- Designed test scenarios and prepared documentation for app publishing.

### General Authentication
- Secure token blacklisting for logout.
- Country-based access control using GeoIP2.
- Token rotation and Redis optimization for scalability.

### Security and Scalability
- Secure token storage and session management.
- Rate limiting and retry mechanisms to handle DDoS attacks.
- Message queue optimization for high loads.

---

## 🌟 **Features**

### Authentication
- 🔑 JWT-based secure login.
- 🔄 Social login (Facebook OAuth2).
- 🚪 Safe logout with token invalidation.
- 🌍 Country-based IP restrictions.
- ⏱️ Session management.

### Communication Channels
- 💬 WhatsApp Business API integration.
- 📧 Email sending via Gmail/Office 365.
- ⚡ Asynchronous messaging.
- 🔄 Retry mechanisms for API errors.

---

## 🛠️ **Tech Stack**

### Backend

#### Core Technologies
- Python 3.8+
- Django 5.1.5 + Django REST Framework 3.15.2
- PostgreSQL (Database) + Redis (Caching & Queue)
- Celery 5.4.0 (Async Task Processing)
- JWT Authentication with Token Blacklisting

#### Project Structure
```
backend/
├── apps/
│   ├── authentication/    # User auth, social login, token management
│   ├── communications/   # Message handling, WhatsApp/Email integration
│   └── core/            # Shared utilities and base classes
├── config/              # Project settings and configuration
└── requirements.txt     # Project dependencies
```

#### Key Components
1. **Authentication System**
   - JWT-based authentication with token rotation
   - Social authentication (Facebook OAuth2)
   - IP-based access control using GeoIP2
   - Token blacklisting for secure logout

2. **Communications Module**
   - WhatsApp message handling via Meta Cloud API
   - Email integration with Gmail/Office 365
   - Asynchronous message processing
   - Rate limiting and retry mechanisms

3. **Task Queue System**
   - Celery for asynchronous task processing
   - Redis as message broker
   - Scheduled tasks with django-celery-beat
   - Error handling and retry mechanisms

#### Key Dependencies
- djangorestframework-simplejwt (5.4.0): JWT authentication
- social-auth-app-django (5.4.2): Social authentication
- celery (5.4.0): Asynchronous task processing
- redis (5.2.1): Caching and message broker
- psycopg2-binary (2.9.10): PostgreSQL adapter
- django-cors-headers (4.6.0): CORS support
- python-dotenv (1.0.1): Environment configuration

#### Development Environment

1. **System Requirements**
   - Python 3.8 or higher
   - SQLite3
   - Redis 5+
   - Git

2. **IDE Recommendations**
   - VSCode with Python extension
   - PyCharm (Community or Professional)

3. **Environment Variables**
   ```
   # Database
   DATABASE_URL=postgresql://user:password@localhost:5432/dbname
   
   # Redis
   REDIS_URL=redis://localhost:6379/0
   
   # JWT Settings
   JWT_SECRET_KEY=your-secret-key
   JWT_ACCESS_TOKEN_LIFETIME=5
   JWT_REFRESH_TOKEN_LIFETIME=1440
   
   # Social Auth
   FACEBOOK_APP_ID=your-app-id
   FACEBOOK_APP_SECRET=your-app-secret
   
   # Communications
   WHATSAPP_API_TOKEN=your-whatsapp-token
   WHATSAPP_PHONE_NUMBER=your-whatsapp-number
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_HOST_USER=your-email
   EMAIL_HOST_PASSWORD=your-app-password
   ```

4. **Development Tools**
   - Black: Code formatting
   - Flake8: Code linting
   - pytest: Testing framework
   - django-debug-toolbar: Development debugging

5. **API Documentation**
   - Available at `/api/docs/` when running in development mode
   - Swagger UI for interactive API testing
   - Detailed endpoint documentation with request/response examples

### Frontend
- Next.js (App Router)
- TypeScript
- Tailwind CSS
- shadcn/ui, lucide-react, motion
- next-auth for authentication

---

## 🚀 **Getting Started**

### Backend Setup
1. Clone the repository:
   ```bash
   git clone [[repository-url]](https://github.com/bulbashenko/message-sender.git)
   cd backend
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   ```bash
   cp .env.example .env
   ```

5. Apply migrations:
   ```bash
   python manage.py migrate
   ```

6. Start Redis (in a separate terminal):
   ```bash
   redis-server
   ```

7. Start Celery worker:
   ```bash
   celery -A config worker -l info
   ```

8. Start the development server:
   ```bash
   python manage.py runserver
   ```

### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   # or
   pnpm install
   ```

3. Configure environment variables:
   ```bash
   cp .env.example .env.local
   ```

4. Start the development server:
   ```bash
   npm run dev
   #or
   pnpm dev
   ```
   
---

## 🐛 **Troubleshooting**

### Common Issues

1. **Redis Connection Error**
   ```bash
   # Ensure Redis is running
   redis-cli ping  # Should return PONG
   ```

2. **Database Migration Issues**
   If you encounter migration errors, follow these steps:

   ```bash
   # Reset and reapply migrations for specific apps
   python manage.py makemigrations authentication communications
   python manage.py migrate
   ```

---


## 🔒 **Security Features**

- JWT-based authentication
- CSRF protection
- Rate limiting
- Data validation
- Password security
- Session management
- IP-based restrictions

---

## 📄 **License**
Distributed under the MIT License. See the [LICENSE](LICENSE) file for more information.
