# InnoEvent - Event Management Platform

<div align="center">

![InnoEvent](https://img.shields.io/badge/FastAPI-0.104.1-009688?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=flat-square)
![Flask](https://img.shields.io/badge/Flask-3.0.0-000000?style=flat-square)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

**A modern, full-stack event management platform with real-time seat tracking and comprehensive observability**

[Features](#-features) • [Quick Start](#-quick-start) • [API Docs](#-api-documentation) • [Deployment](#-deployment) • [Tech Stack](#-technology-stack)

</div>

---

## 📋 About

**InnoEvent** is a comprehensive event management platform designed for organizations to create, manage, and register users for internal events. The platform provides real-time seat availability tracking, user management, and complete observability with structured logging and metrics collection.

Built with **FastAPI** (backend) and **Flask** (frontend), InnoEvent demonstrates modern web development practices including RESTful API design, database management, and production-ready observability.

---

## ✨ Features

- 👤 **User Management**
  - User registration and authentication
  - Profile management
  - User activity tracking

- 📅 **Event Management**
  - Create, read, update, and delete events
  - Support for multiple event types (Meetup, Conference, Concert)
  - Real-time seat availability tracking
  - Event organization and filtering

- 📝 **Event Registration**
  - Register/unregister for events
  - Real-time seat capacity management
  - Prevent double registration
  - View registration history

- 📊 **Observability & Monitoring**
  - Structured JSON logging (app.log, errors.log)
  - Application metrics collection (/metrics endpoint)
  - Health checks (/health, /health/detailed)
  - Request performance tracking
  - Error rate monitoring

- 🎨 **User Interface**
  - Modern, responsive design
  - Montserrat font styling
  - Intuitive event browsing and registration
  - Real-time UI updates

- 🐳 **DevOps Ready**
  - Docker and Docker Compose support
  - Easy local and production deployment
  - Quick start script (run.bat for Windows)

---

## 🏗️ Architecture

```
InnoEvent/
├── backend/                    # FastAPI Backend
│   ├── main.py                # FastAPI application
│   ├── models.py              # SQLAlchemy database models
│   ├── schemas.py             # Pydantic validation schemas
│   ├── crud.py                # Database CRUD operations
│   ├── database.py            # Database configuration
│   ├── logging_config.py      # Structured logging setup
│   ├── metrics.py             # Application metrics
│   ├── requirements.txt       # Python dependencies
│   ├── Dockerfile             # Backend container
│   └── innoevent.db           # SQLite database
│
├── frontend/                   # Flask Frontend
│   ├── app.py                 # Flask application
│   ├── index.html             # Main HTML template
│   ├── script.js              # Frontend logic
│   ├── style.css              # Styling (Montserrat)
│   ├── requirements.txt       # Python dependencies
│   ├── Dockerfile             # Frontend container
│   ├── background.png         # Background image
│   └── logo.png               # Application logo
│
├── db/                        # Database Configuration
│   ├── Dockerfile
│   └── init.sql
│
├── docker-compose.yml         # Docker orchestration
├── run.bat                    # Windows quick start
└── README.md                  # This file
```

### Database Schema

```sql
-- Users Table
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    surname VARCHAR(100) NOT NULL,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(20),
    password VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Events Table
CREATE TABLE events (
    id INTEGER PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    event_type VARCHAR(50) NOT NULL,
    event_date DATETIME NOT NULL,
    location VARCHAR(200),
    total_seats INTEGER NOT NULL,
    available_seats INTEGER NOT NULL,
    organizer_id INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (organizer_id) REFERENCES users(id)
);

-- Registrations Table
CREATE TABLE registrations (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    event_id INTEGER NOT NULL,
    registered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (event_id) REFERENCES events(id)
);
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Git
- Docker & Docker Compose (optional, for containerized deployment)

### Option 1: Windows Quick Start (Recommended)

```bash
cd InnoEvent
run.bat
```

This automatically:
1. Creates virtual environments
2. Installs dependencies
3. Starts both frontend and backend servers

---

### Option 2: Manual Setup

#### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the backend server
python main.py
```

**Backend URL:** `http://localhost:8000`

#### Frontend Setup (in a new terminal)

```bash
# Navigate to frontend directory
cd frontend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the frontend server
python app.py
```

**Frontend URL:** `http://localhost:3000`

---

### Option 3: Docker Compose Deployment

```bash
docker-compose up --build
```

Services:
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Swagger Docs:** http://localhost:8000/docs

---

## 📚 API Documentation

### Base URL
```
http://localhost:8000/api
```

### Authentication Endpoints

**Register New User**
```http
POST /auth/register
Content-Type: application/json

{
  "surname": "Menshikh",
  "name": "Maksim",
  "email": "maksim@example.com",
  "phone": "+1234567890",
  "password": "password123"
}

Response: 201 Created
{
  "id": 1,
  "surname": "Menshikh",
  "name": "Maksim",
  "email": "maksim@example.com",
  "phone": "+1234567890",
  "created_at": "2025-11-28T07:00:00"
}
```

**User Login**
```http
POST /auth/login
Content-Type: application/x-www-form-urlencoded

email=maksim@example.com&password=password123

Response: 200 OK
{
  "id": 1,
  "surname": "Menshikh",
  "name": "Maksim",
  "email": "maksim@example.com",
  "phone": "+1234567890",
  "created_at": "2025-11-28T07:00:00"
}
```

### Event Endpoints

**List All Events**
```http
GET /events
GET /events?event_type=Meetup

Response: 200 OK
[
  {
    "id": 1,
    "title": "Python Meetup",
    "description": "Monthly Python developers meetup",
    "event_type": "Meetup",
    "event_date": "2025-11-30T18:00:00",
    "location": "Tech Hub, Room 101",
    "total_seats": 50,
    "available_seats": 35,
    "organizer_id": 1,
    "created_at": "2025-11-28T07:00:00"
  }
]
```

**Create Event**
```http
POST /events?organizer_id=1
Content-Type: application/json

{
  "title": "AI Conference 2025",
  "description": "Annual artificial intelligence conference",
  "event_type": "Conference",
  "event_date": "2025-12-10T09:00:00",
  "location": "Convention Center",
  "total_seats": 500
}

Response: 200 OK
{
  "id": 2,
  "title": "AI Conference 2025",
  "description": "Annual artificial intelligence conference",
  "event_type": "Conference",
  "event_date": "2025-12-10T09:00:00",
  "location": "Convention Center",
  "total_seats": 500,
  "available_seats": 500,
  "organizer_id": 1,
  "created_at": "2025-11-28T07:30:00"
}
```

**Update Event**
```http
PUT /events/1
Content-Type: application/json

{
  "total_seats": 60,
  "available_seats": 45
}

Response: 200 OK
```

**Delete Event**
```http
DELETE /events/1

Response: 204 No Content
```

### Registration Endpoints

**Register for Event**
```http
POST /registrations?user_id=1
Content-Type: application/json

{
  "event_id": 1
}

Response: 201 Created
{
  "id": 1,
  "user_id": 1,
  "event_id": 1,
  "registered_at": "2025-11-28T08:00:00"
}
```

**Get User Registrations**
```http
GET /registrations/user/1

Response: 200 OK
[
  {
    "id": 1,
    "user_id": 1,
    "event_id": 1,
    "registered_at": "2025-11-28T08:00:00",
    "event": { /* event object */ }
  }
]
```

**Cancel Registration**
```http
DELETE /registrations/1

Response: 204 No Content
```

### Monitoring Endpoints

**Health Check**
```http
GET /health

Response: 200 OK
{
  "status": "ok",
  "timestamp": "2025-11-28T08:15:00.123456",
  "service": "InnoEvent API"
}
```

**Detailed Health Check**
```http
GET /health/detailed

Response: 200 OK
{
  "status": "healthy",
  "timestamp": "2025-11-28T08:15:00.123456",
  "service": "InnoEvent API",
  "version": "1.0.0",
  "metrics": { /* metrics object */ }
}
```

**Application Metrics**
```http
GET /metrics

Response: 200 OK
{
  "uptime_seconds": 3600.5,
  "total_requests": 2500,
  "total_errors": 15,
  "error_rate": 0.6,
  "total_registrations": 342,
  "avg_response_time_ms": 45.3,
  "requests_by_endpoint": {
    "/api/events": 1200,
    "/api/registrations": 800
  },
  "errors_by_type": {
    "404": 8,
    "400": 5,
    "500": 2
  },
  "timestamp": "2025-11-28T08:15:00.123456"
}
```

### Full API Documentation

Interactive API documentation available at:
```
http://localhost:8000/docs
```

---

## 📊 Logging & Observability

### Logging Configuration

Logs are stored in `backend/logs/` directory:

- **app.log** - JSON structured logs of all application events
- **errors.log** - Error-level logs only

#### Log Format Example
```json
{
  "timestamp": "2025-11-28T08:15:30.123456",
  "level": "INFO",
  "logger": "innoevent",
  "message": "User registered for event",
  "module": "crud",
  "function": "register_user_for_event",
  "line": 245
}
```

### Metrics Collection

The application tracks:
- **Request Metrics** - Total requests, requests by endpoint
- **Error Metrics** - Error count, error rate, errors by type
- **Performance Metrics** - Average response time, response times by request
- **System Metrics** - Uptime, application start time
- **Business Metrics** - Total registrations, total events created

Access metrics: `GET /metrics`

---

## 🛠️ Technology Stack

### Backend
- **Framework:** FastAPI 0.104.1 (Python web framework)
- **Database:** SQLite with SQLAlchemy ORM
- **Validation:** Pydantic v2
- **API Server:** Uvicorn
- **Logging:** Python Logging with JSON formatting
- **Monitoring:** Custom metrics collection

### Frontend
- **Framework:** Flask 3.0.0
- **Template:** HTML5 with Jinja2
- **Styling:** CSS3 with Montserrat font
- **Scripting:** Vanilla JavaScript (ES6+)
- **Client-side routing:** Custom JavaScript
- **HTTP Client:** Fetch API

### DevOps
- **Containerization:** Docker
- **Orchestration:** Docker Compose
- **Version Control:** Git & GitHub

### Development Tools
- **Package Management:** pip
- **Virtual Environments:** venv
- **Testing:** Manual testing via Swagger UI

---

## 📈 Key Features Implementation

### Real-time Seat Tracking
- When a user registers, `available_seats` decreases by 1
- When total seats are updated, available seats recalculate
- When a registration is cancelled, `available_seats` increases by 1

### User Registration
- Email uniqueness validation
- Name and surname uniqueness validation
- Prevention of duplicate event registrations

### Event Management
- Support for multiple event types (Meetup, Conference, Concert)
- Event date tracking with timezone handling
- Location-based event organization

### Observability
- Structured JSON logging for easy parsing and analysis
- Comprehensive metrics for monitoring application health
- Health check endpoints for uptime monitoring
- Error tracking by type for better debugging

---

## 🗄️ Database Management

### Clear All Data (Keep Database Structure)
```bash
cd backend
python clear_data.py
```

### Full Database Reset (Delete & Recreate)
```bash
cd backend
# On Windows:
del innoevent.db
# On macOS/Linux:
rm innoevent.db

python main.py
```

---

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Find process using port 8000 (backend)
netstat -ano | findstr :8000

# Find process using port 3000 (frontend)
netstat -ano | findstr :3000

# Kill process by PID
taskkill /PID <PID> /F
```

### Virtual Environment Issues
```bash
# Delete venv and recreate
rmdir /s venv
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Database Errors
```bash
# Reset database
cd backend
del innoevent.db
python main.py
```

### Docker Issues
```bash
# Clean up Docker containers and images
docker-compose down
docker system prune -a

# Rebuild from scratch
docker-compose up --build --force-recreate
```

---

## 📋 Project Requirements Checklist

| Requirement | Status | Details |
|------------|--------|---------|
| Frontend Development | ✅ Complete | Flask + HTML/CSS/JS, Montserrat font, responsive design |
| Backend Development | ✅ Complete | FastAPI with SQLAlchemy ORM, RESTful API |
| Database Design | ✅ Complete | SQLite with 3 tables (users, events, registrations) |
| Observability | ✅ Complete | Structured JSON logging, metrics collection, health checks |
| Seat Management | ✅ Complete | Real-time seat tracking and availability management |
| User Authentication | ✅ Complete | Registration and login functionality |
| Event Registration | ✅ Complete | Create, update, delete registrations with validation |
| Lean Canvas | ⏳ Pending | Business model documentation (deadline: Nov 28) |
| Unit Economics | ⏳ Pending | Revenue and cost analysis (deadline: Nov 28) |

---

## 🚀 Deployment

### Local Deployment
- Run `run.bat` (Windows) or manual setup steps
- Access frontend at http://localhost:3000
- Backend API at http://localhost:8000

### Docker Deployment
- Run `docker-compose up --build`
- All services start automatically
- Logs visible in terminal

### Production Deployment (Future)
- Deploy to cloud platforms (AWS, GCP, Azure)
- Use environment variables for configuration
- Set up CI/CD pipeline with GitHub Actions
- Implement SSL/TLS certificates
- Use production-grade database (PostgreSQL)
- Set up monitoring and alerting

---

## 📝 File Structure & Descriptions

```
backend/
├── main.py              # FastAPI application entry point
├── models.py            # SQLAlchemy ORM models (User, Event, Registration)
├── schemas.py           # Pydantic validation schemas
├── crud.py              # Database CRUD operations
├── database.py          # Database configuration and session management
├── logging_config.py    # Structured JSON logging setup
├── metrics.py           # Application metrics collection class
├── requirements.txt     # Python dependencies
├── Dockerfile           # Container image definition
└── innoevent.db         # SQLite database file

frontend/
├── app.py               # Flask application server
├── index.html           # Main HTML template
├── script.js            # Frontend JavaScript logic and API calls
├── style.css            # CSS styling with Montserrat font
├── requirements.txt     # Python dependencies
├── Dockerfile           # Container image definition
├── background.png       # Background image asset
└── logo.png             # Application logo asset
```

---

## 🎓 Learning Outcomes

This project demonstrates:
- Full-stack web application development
- RESTful API design and implementation
- Database design and ORM usage
- Frontend-backend integration
- Structured logging and observability
- Docker containerization
- Git version control
- Professional code organization
- User authentication and authorization patterns

---

## 📄 License

This project is part of the MTC True Tech+ Program.

---

## 👥 Contributing

For questions or suggestions, please contact the development team.

---

## 📞 Support & Contact

For issues or feature requests:
1. Check existing GitHub issues
2. Review the troubleshooting section
3. Contact the development team

---

<div align="center">

**Built with ❤️ for event management**

[Back to top](#innoevent---event-management-platform)

**Last Updated:** November 28, 2025 | **Version:** 1.0.0

</div>
