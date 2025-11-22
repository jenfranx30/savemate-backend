# SaveMate Backend API

**Modern Python/FastAPI backend for SaveMate - Local Deals Platform**

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)](https://fastapi.tiangolo.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-7.0%2B-brightgreen.svg)](https://www.mongodb.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Table of Contents

- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [Features](#features)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Server](#running-the-server)
- [API Documentation](#api-documentation)
- [Database Schema](#database-schema)
- [Development](#development)
- [Testing](#testing)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [Team](#team)

---

## Overview

SaveMate is a location-based deals platform that helps users discover local promotions and discounts. This repository contains the backend API built with FastAPI, MongoDB, and modern Python best practices.

**Key Highlights:**
- ⚡ High-performance async FastAPI framework
- 🗄️ MongoDB with Beanie ODM for flexible data modeling
- 🔐 JWT-based authentication with secure password hashing
- 📍 Geospatial queries for location-based deal discovery
- 📸 Cloud-based image storage with Cloudinary
- 📚 Automatic interactive API documentation (Swagger UI)
- 🎨 Type-safe with Pydantic models and Python type hints

---

## Tech Stack

### **Core Framework**
- **FastAPI** (0.104.1) - Modern, fast web framework for building APIs
- **Uvicorn** (0.24.0) - ASGI server for production-ready performance
- **Python** (3.11+) - Latest Python with enhanced performance

### **Database**
- **MongoDB** (7.0+) - NoSQL database for flexible data storage
- **Motor** (3.3.2) - Async MongoDB driver
- **Beanie** (1.23.6) - Async ODM for MongoDB with Pydantic integration

### **Authentication & Security**
- **python-jose** (3.3.0) - JWT token generation and validation
- **passlib[bcrypt]** (1.7.4) - Secure password hashing
- **python-multipart** (0.0.6) - File upload support

### **Data Validation**
- **Pydantic** (2.5.0) - Data validation using Python type hints
- **pydantic-settings** (2.1.0) - Settings management
- **email-validator** (2.1.0) - Email validation

### **Cloud Services**
- **Cloudinary** (1.36.0) - Image upload and optimization

### **Development Tools**
- **pytest** (7.4.3) - Testing framework
- **black** (23.12.0) - Code formatting
- **flake8** (6.1.0) - Linting

---

## Features

### **Implemented (Phase 1 ✅)**
- [x] FastAPI application with CORS support
- [x] MongoDB connection with async support
- [x] Environment-based configuration
- [x] Automatic API documentation (Swagger UI & ReDoc)
- [x] Health check endpoints
- [x] Project structure with best practices

### **Work in Progress (Phase 2-4)**
- [ ] User authentication (register, login, JWT)
- [ ] User profile management
- [ ] Deal CRUD operations
- [ ] Business management
- [ ] Category system
- [ ] Geospatial queries (nearby deals)
- [ ] Image upload with Cloudinary
- [ ] Search and filtering
- [ ] Rate limiting
- [ ] Comprehensive test coverage

---

## 📁 Project Structure

```
savemate-backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration and settings
│   ├── database.py             # MongoDB connection setup
│   │
│   ├── models/                 # Beanie document models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── deal.py
│   │   ├── business.py
│   │   └── category.py
│   │
│   ├── schemas/                # Pydantic schemas (request/response)
│   │   ├── __init__.py
│   │   ├── user_schema.py
│   │   ├── deal_schema.py
│   │   ├── auth_schema.py
│   │   └── common_schema.py
│   │
│   ├── api/                    # API route handlers
│   │   ├── __init__.py
│   │   ├── deps.py             # Dependencies (auth, etc.)
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── auth.py
│   │       ├── users.py
│   │       ├── deals.py
│   │       ├── businesses.py
│   │       └── categories.py
│   │
│   ├── services/               # Business logic layer
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── user_service.py
│   │   ├── deal_service.py
│   │   └── cloudinary_service.py
│   │
│   ├── utils/                  # Utility functions
│   │   ├── __init__.py
│   │   ├── security.py
│   │   └── validators.py
│   │
│   └── middleware/             # Custom middleware
│       ├── __init__.py
│       └── error_handler.py
│
├── tests/                      # Test files
│   ├── test_auth.py
│   ├── test_deals.py
│   └── test_users.py
│
├── .env                        # Environment variables (not in git)
├── .env.example               # Environment variables template
├── .gitignore                 # Git ignore rules
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

---

## Prerequisites

Before you begin, ensure you have:

- **Python 3.11+** installed ([Download](https://www.python.org/downloads/))
- **MongoDB Atlas** account (free tier) or local MongoDB
- **Git** installed
- **Code editor** (VS Code recommended)

---

## Installation

### **1. Clone the Repository**

```bash
git clone https://github.com/jenfranx30/savemate-backend.git
cd savemate-backend
```

### **2. Create Virtual Environment (Optional but Recommended)**

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### **3. Install Dependencies**

```bash
pip install -r requirements.txt
```

---

## Configuration

### **1. Create .env File**

Copy the example environment file:

```bash
cp .env.example .env
```

### **2. Configure Environment Variables**

Edit `.env` file with your settings:

```env
# MongoDB Configuration
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
DATABASE_NAME=savemate

# JWT Configuration
SECRET_KEY=your-super-secret-key-here-min-32-characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Cloudinary Configuration
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# Application Configuration
DEBUG=True
API_V1_PREFIX=/api/v1
PROJECT_NAME=SaveMate API

# Server Configuration
HOST=0.0.0.0
PORT=8000
```

### **3. Generate Secure SECRET_KEY**

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy the output and paste it as your `SECRET_KEY` in `.env`.

### **4. Set Up MongoDB Atlas (Free)**

1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas/register)
2. Create a FREE M0 cluster
3. Create a database user
4. Whitelist your IP (0.0.0.0/0 for development)
5. Get your connection string
6. Update `MONGODB_URL` in `.env`

---

## Running the Server

### **Development Mode (with auto-reload)**

```bash
uvicorn app.main:app --reload
```

### **Production Mode**

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### **Custom Port**

```bash
uvicorn app.main:app --reload --port 8001
```

### **Expected Output**

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
🚀 Starting SaveMate API...
✅ Connected to MongoDB database: savemate
INFO:     Application startup complete.
```

---

## API Documentation

Once the server is running, access the interactive API documentation:

### **Swagger UI (Interactive)**
```
http://localhost:8000/docs
```

### **ReDoc (Alternative)**
```
http://localhost:8000/redoc
```

### **OpenAPI JSON Schema**
```
http://localhost:8000/openapi.json
```

### **Health Check**
```
http://localhost:8000/health
```

---

## Database Schema

### **Collections**

1. **users** - User accounts and profiles
2. **deals** - Local deals and promotions
3. **businesses** - Business information
4. **categories** - Deal categories

### **Key Features**
- Geospatial indexes for location-based queries
- Text indexes for search functionality
- Reference relationships between collections
- Automatic timestamp management

---

## Development

### **Code Formatting**

```bash
black app/
```

### **Linting**

```bash
flake8 app/
```

### **Type Checking**

```bash
mypy app/
```

---

## Testing

### **Run All Tests**

```bash
pytest
```

### **Run with Coverage**

```bash
pytest --cov=app tests/
```

### **Run Specific Test File**

```bash
pytest tests/test_auth.py
```

---

## Deployment

### **Recommended Platforms**

1. **Render** - Easy Python deployment
2. **Railway** - Simple and fast
3. **Heroku** - Classic PaaS
4. **AWS/GCP/Azure** - Full control

### **Environment Variables**

Make sure to set all required environment variables in your deployment platform:
- `MONGODB_URL`
- `SECRET_KEY`
- `ALLOWED_ORIGINS` (update with production URL)
- `DEBUG=False`

### **Production Checklist**

- [ ] Set `DEBUG=False`
- [ ] Use strong `SECRET_KEY`
- [ ] Configure CORS with specific origins
- [ ] Set up MongoDB Atlas production cluster
- [ ] Enable SSL/TLS
- [ ] Set up monitoring and logging
- [ ] Configure rate limiting
- [ ] Set up backup strategy

---

## Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### **Coding Standards**

- Follow PEP 8 style guide
- Write docstrings for all functions/classes
- Add type hints
- Write tests for new features
- Update documentation

---

## 👥 Team

**SaveMate Development Team**

- **Rustam Islamov** - Team Leader and Backend Developer
- **Jenefer Yago** - Documentation and Full Stack Developer
- **Mahammad Rustamov** - Frontend Developer
- **Rustam Yariyev** - API Development
- **Sadig Shikhaliyev** - API Development
  
**Course**: Agile Project Management
**Professor**: Dawid Jurczyński
**University**: WSB University, Dąbrowa Górnicza  
**Semester**: Winter 2025-2026


---

## Acknowledgments

- FastAPI for the amazing framework
- MongoDB for flexible data storage
- WSB University for project guidance
- All contributors and team members

---

## 📈 Project Status

**Current Phase**: Phase 1 Complete ✅  
**Next Phase**: Database Models and Authentication  
**Target Completion**: January 2026

---

## Related Repositories

- [SaveMate Frontend](https://github.com/jenfranx30/savemate-frontend) - React application
- [SaveMate Docs](https://github.com/jenfranx30/savemate-docs) - Project documentation

---

*Last Updated: November 22, 2025*
