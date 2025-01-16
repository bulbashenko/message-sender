# Full-Stack Authentication and Communication System

A modern full-stack application featuring a Next.js frontend and Django backend, providing robust authentication and communication capabilities including WhatsApp and email integration.

## Project Structure

- `frontend/` - Next.js frontend application
- `backend/` - Django backend with authentication and communications APIs

## Key Features

### Frontend (Next.js)
- Modern React-based UI with Next.js 13+
- Server-side rendering capabilities
- Optimized font loading with next/font
- Responsive and interactive user interface

### Backend (Django)
- **Authentication System**
  - Token-based authentication with JWT
  - Token blacklisting for secure logout
  - Facebook OAuth integration
  - IP-based country restrictions

- **Communication Features**
  - WhatsApp integration via Meta Cloud API
  - Email integration with Gmail SMTP
  - Asynchronous message handling with Celery
  - Message tracking and status monitoring

## Setup Instructions

### Backend Setup

1. Set up Python virtual environment:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install backend dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment:
- Copy `backend/.env.example` to `backend/.env`
- Fill in required credentials and API keys

4. Set up Redis for Celery:
- Install Redis
- Ensure Redis server is running on localhost:6379

5. Run migrations:
```bash
python manage.py migrate
```

6. Start the Django server:
```bash
python manage.py runserver
```

7. Start Celery worker:
```bash
celery -A config worker -l info
```

### Frontend Setup

1. Install frontend dependencies:
```bash
cd frontend
npm install
# or
yarn install
```

2. Start the development server:
```bash
npm run dev
# or
yarn dev
```

The frontend will be available at [http://localhost:3000](http://localhost:3000)

## Environment Configuration

### Backend Environment Variables
See `backend/.env.example` for required variables:
- Django configuration
- Database settings
- Email (Gmail) credentials
- Facebook OAuth credentials
- WhatsApp API configuration
- Celery settings

## API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `POST /api/auth/facebook/` - Facebook OAuth login

### Communication
- WhatsApp and Email functionalities available through the communications app
- Utility functions provided in `communications.utils`

## Development Setup

### Gmail Configuration
1. Enable "Less secure app access" or create an App Password
2. Add Gmail credentials to backend/.env

### Facebook OAuth Setup
1. Create a Facebook App
2. Configure OAuth settings
3. Add credentials to backend/.env

### WhatsApp Integration
1. Set up Meta Cloud API
2. Configure WhatsApp business account
3. Add API credentials to backend/.env

## Testing

Backend testing utilities available:
- `whatsapp_test.py` - Test WhatsApp integration
- `smtp_test.py` - Test email functionality

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request