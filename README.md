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
- Python 3.8+
- Django 5.1.5 + DRF 3.15.2
- PostgreSQL + Redis
- Celery 5.4.0
- JWT Authentication

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

Теперь этот раздел включает шаги для исправления проблем с миграциями. Если еще что-то нужно уточнить или дополнить, дай знать!

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
