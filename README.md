# Communication and Authentication System 🔐📱

A robust, scalable system for handling user authentication and multi-channel communications, built with Django and Next.js. This project implements secure authentication mechanisms, social login capabilities, and multi-channel messaging through WhatsApp and Email.

![Project Banner](frontend/public/globe.svg)

## 🌟 Features

### Authentication System
- 🔑 Token-based authentication with JWT
- 🔄 Social media integration (Facebook OAuth2)
- 🚪 Secure logout with token blacklisting
- 🌍 IP-based access restrictions by country
- 🔒 Password strength validation
- ⏱️ Session management

### Communication Channels
- 💬 WhatsApp Business API integration
- 📧 Email system integration (Gmail/Office 365)
- ⚡ Asynchronous message processing
- 📊 Message delivery tracking
- 🔄 Error handling and retry mechanisms

## 🛠️ Tech Stack

### Backend (Django)
- Python 3.8+
- Django REST Framework
- PostgreSQL
- Redis
- Celery
- JWT Authentication

### Frontend (Next.js)
- React 18+
- TypeScript
- Tailwind CSS
- Shadcn UI
- Next.js 13+ (App Router)

## 🚀 Getting Started

### Prerequisites
```bash
Python 3.8+
Node.js 16+
Redis Server
PostgreSQL
```

### Backend Setup

1. Clone the repository
```bash
git clone [repository-url]
cd backend
```

2. Create and activate virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Configure environment variables
```bash
cp .env.example .env
# Edit .env with your configurations
```

Required environment variables:
```env
DEBUG=True
REDIS_URL=redis://localhost:6379/0
FACEBOOK_APP_ID=your-facebook-app-id
FACEBOOK_APP_SECRET=your-facebook-app-secret
```

5. Run migrations
```bash
python manage.py migrate
```

6. Start development server
```bash
python manage.py runserver
```

### Frontend Setup

1. Navigate to frontend directory
```bash
cd frontend
```

2. Install dependencies
```bash
npm install
```

3. Configure environment variables
```bash
cp .env.example .env.local
# Edit .env.local with your configurations
```

Required environment variables:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_FACEBOOK_APP_ID=your-facebook-app-id
```

4. Start development server
```bash
npm run dev
```

## 🏗️ Architecture

### Backend Architecture
The backend follows Clean Architecture principles and SOLID design patterns:

#### Apps Structure
```
backend/
├── apps/
│   ├── authentication/    # User authentication
│   ├── communications/    # Message handling
│   └── core/             # Shared functionality
└── config/               # Project configuration
```

### Frontend Architecture
```
frontend/
├── app/                  # Next.js 13+ App Router
│   ├── auth/            # Authentication pages
│   ├── dashboard/       # User dashboard
│   └── components/      # Reusable components
├── lib/                 # Utilities and helpers
└── public/              # Static assets
```

## 🔒 Security Features

- JWT token management
- CSRF protection
- Rate limiting
- Input validation
- Secure password handling
- Session security
- IP-based restrictions

## 🚦 Development Workflow

1. Create a new branch for your feature
```bash
git checkout -b feature/your-feature-name
```

2. Make your changes and commit using conventional commits
```bash
git commit -m "feat: add new feature"
git commit -m "fix: resolve bug issue"
```

3. Push changes and create a pull request
```bash
git push origin feature/your-feature-name
```

## 🐛 Troubleshooting

### Common Issues

1. **Redis Connection Error**
```bash
# Ensure Redis is running
redis-cli ping  # Should return PONG
```

2. **Database Migration Issues**
```bash
# Reset migrations
python manage.py migrate --fake authentication zero
python manage.py migrate authentication
```

3. **Frontend API Connection Issues**
- Check if backend server is running
- Verify environment variables
- Check CORS settings in backend

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes using conventional commits
4. Push to your branch
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 💬 Support

For support and questions:
- 📚 Review [documentation](docs/)
- 🐛 Check [issue tracker](issues/)
- 📧 Contact development team

---

<div align="center">
Built with ❤️ using Django, Next.js, and modern web technologies.

![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)
![Next JS](https://img.shields.io/badge/Next-black?style=for-the-badge&logo=next.js&logoColor=white)
![TypeScript](https://img.shields.io/badge/typescript-%23007ACC.svg?style=for-the-badge&logo=typescript&logoColor=white)
</div>