# SaveMate Backend API

**Modern Python/FastAPI backend for SaveMate - Local Deals Platform**

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)](https://fastapi.tiangolo.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-7.0%2B-brightgreen.svg)](https://www.mongodb.com/)

---

# Project Overview

A local deals and discounts platform backend built with FastAPI and MongoDB. SaveMate helps users discover and save money on local deals in their area.

The backend API provides authentication, user management, and will include deal discovery, business management and location-based features.

**Course:** Agile Project Management 
**Methodology:** Kanban  
**Duration:** November 2025 - January 2026  
**Project Management:** Trello

## ✅ Development Status

### Phase 1: Project Setup (Complete)
- ✅ Project structure created
- ✅ Git repository initialized
- ✅ MongoDB Atlas configured
- ✅ Environment setup

### Phase 2: Database Models (Complete)
- ✅ User model with Beanie ODM
- ✅ MongoDB connection established
- ✅ Database schemas designed

### Phase 3: Authentication System (Complete)
- ✅ User registration endpoint
- ✅ Login with email/username support
- ✅ JWT token authentication
- ✅ Token refresh mechanism
- ✅ Password hashing with bcrypt
- ✅ Pydantic validation schemas
- ✅ Swagger UI documentation

### Phase 4: Coming Soon
- 🔄 Deals management
- 🔄 Business profiles
- 🔄 Location-based features

---

## Tech Stack

- **Framework:** FastAPI 0.104+
- **Database:** MongoDB with Beanie ODM
- **Authentication:** JWT (JSON Web Tokens)
- **Password Hashing:** bcrypt 4.1.2
- **Validation:** Pydantic
- **Documentation:** Swagger UI (auto-generated)
- **Server:** Uvicorn

---

## Installation & Setup

### Prerequisites

- Python 3.8+
- MongoDB Atlas account (or local MongoDB)
- Git

### Step 1: Clone the Repository
```bash
git clone https://github.com/jenfranx30/savemate-backend.git
cd savemate-backend
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

**Key packages installed:**
```
fastapi==0.104.1
uvicorn==0.24.0
beanie==1.23.6
motor==3.3.2
pydantic==2.5.0
pydantic-settings==2.1.0
python-jose[cryptography]==3.3.0
passlib==1.7.4
bcrypt==4.1.2
python-dotenv==1.0.0
```

### Step 4: Environment Configuration

Create a `.env` file in the root directory:
```env
# MongoDB Configuration
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/savemate?retryWrites=true&w=majority

# JWT Configuration
JWT_SECRET=your-super-secret-key-minimum-32-characters-long
JWT_REFRESH_SECRET=your-refresh-secret-also-minimum-32-characters
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Server Configuration
HOST=127.0.0.1
PORT=8000
```

**Important:** Never commit `.env` to Git! It's in `.gitignore`.

### Step 5: Run the Server
```bash
uvicorn app.main:app --reload
```

**Expected output:**
```
✓ Starting SaveMate API...
✓ Connected to MongoDB database: savemate
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Step 6: Access API Documentation

Open your browser and navigate to:
```
http://localhost:8000/docs
```

You'll see the interactive Swagger UI with all available endpoints!

---

## Authentication Endpoints

### 1. Register New User

**Endpoint:** `POST /api/v1/auth/register`

**Request Body:**
```json
{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "SecurePass123!",
  "full_name": "John Doe",
  "is_business_owner": false
}
```

**Response (201 Created):**
```json
{
  "message": "User registered successfully",
  "tokens": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
  },
  "user": {
    "id": "507f1f77bcf86cd799439011",
    "email": "user@example.com",
    "username": "johndoe",
    "full_name": "John Doe",
    "is_business_owner": false,
    "created_at": "2025-11-23T20:47:42.427076"
  }
}
```

### 2. Login

**Endpoint:** `POST /api/v1/auth/login`

**Request Body:**
```json
{
  "email_or_username": "johndoe",
  "password": "SecurePass123!"
}
```

**Response (200 OK):**
```json
{
  "message": "Login successful",
  "tokens": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
  },
  "user": {
    "id": "507f1f77bcf86cd799439011",
    "email": "user@example.com",
    "username": "johndoe",
    "full_name": "John Doe",
    "is_business_owner": false
  }
}
```

### 3. Refresh Token

**Endpoint:** `POST /api/v1/auth/refresh`

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

## Project Structure
```
savemate-backend/
├── app/
│   ├── __init__.py
│   ├── main.py                      # FastAPI application entry point
│   │
│   ├── core/                        # Core functionality
│   │   ├── __init__.py
│   │   ├── security.py              # Password hashing, JWT tokens
│   │   └── config.py                # Configuration settings
│   │
│   ├── models/                      # Database models (Beanie)
│   │   ├── __init__.py
│   │   └── user.py                  # User document model
│   │
│   ├── schemas/                     # Pydantic schemas
│   │   ├── __init__.py
│   │   └── auth_schema.py           # Authentication request/response models
│   │
│   ├── api/                         # API routes
│   │   ├── __init__.py
│   │   └── routes/
│   │       ├── __init__.py
│   │       └── auth.py              # Authentication endpoints
│   │
│   └── db/                          # Database configuration
│       ├── __init__.py
│       └── database.py              # MongoDB connection
│
├── .env                             # Environment variables (not in Git)
├── .gitignore                       # Git ignore file
├── requirements.txt                 # Python dependencies
└── README.md                        # This file
```

---

## Testing with Swagger UI

1. **Start the server:**
```bash
   uvicorn app.main:app --reload
```

2. **Open Swagger UI:**
```
   http://localhost:8000/docs
```

3. **Test Registration:**
   - Find `POST /api/v1/auth/register`
   - Click "Try it out"
   - Enter user data
   - Click "Execute"
   - Copy the `access_token` from response

4. **Test Login:**
   - Find `POST /api/v1/auth/login`
   - Click "Try it out"
   - Enter email/username and password
   - Click "Execute"
   - Copy the `refresh_token`

5. **Test Token Refresh:**
   - Find `POST /api/v1/auth/refresh`
   - Click "Try it out"
   - Paste the `refresh_token`
   - Click "Execute"
   - You'll get new tokens!

---

## 🔒 Security Features

- **Password Hashing:** Bcrypt with salt rounds
- **JWT Tokens:** Secure token-based authentication
- **Token Expiration:** 
  - Access tokens: 30 minutes
  - Refresh tokens: 7 days
- **Password Validation:** Minimum 8 characters
- **Email Validation:** Proper email format required
- **Username Validation:** Alphanumeric with underscores only

---

## Troubleshooting

### Issue: Server won't start

**Solution:**
```bash
# Check if port 8000 is already in use
# Windows:
netstat -ano | findstr :8000

# Kill the process if needed
taskkill /PID <process_id> /F
```

### Issue: MongoDB connection error

**Solution:**
- Check your `MONGODB_URI` in `.env`
- Verify your MongoDB Atlas IP whitelist
- Test connection string separately

### Issue: bcrypt error "password cannot be longer than 72 bytes"

**Solution:**
```bash
pip uninstall -y passlib bcrypt
pip install passlib==1.7.4 bcrypt==4.1.2
```

### Issue: Module not found errors

**Solution:**
```bash
# Clear Python cache
for /d /r . %d in (__pycache__) do @if exist "%d" rmdir /s /q "%d"

# Reinstall requirements
pip install -r requirements.txt
```

---

## 🌍 API Endpoints Overview

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/` | Root endpoint | No |
| GET | `/health` | Health check | No |
| GET | `/api/v1` | API info | No |
| POST | `/api/v1/auth/register` | Register new user | No |
| POST | `/api/v1/auth/login` | Login user | No |
| POST | `/api/v1/auth/refresh` | Refresh token | No |

*More endpoints coming in Phase 4!*

---

## Database Schema

### User Model
```python
{
  "_id": ObjectId,
  "email": string (unique, indexed),
  "username": string (unique, indexed),
  "password_hash": string,
  "full_name": string,
  "is_business_owner": boolean,
  "is_active": boolean,
  "is_verified": boolean,
  "created_at": datetime,
  "updated_at": datetime
}
```

---

## Deployment

### MongoDB Atlas Setup

1. Create account at https://mongodb.com/cloud/atlas
2. Create a cluster
3. Add database user
4. Whitelist IP address (0.0.0.0/0 for development)
5. Get connection string
6. Update `MONGODB_URI` in `.env`

### Production Considerations

- Use strong JWT secrets (32+ characters)
- Enable HTTPS
- Set proper CORS origins
- Use environment-specific configurations
- Implement rate limiting
- Add logging and monitoring
- Regular database backups

---

## 👥 Team

- **Project Lead:** [Rustam Islamov]
- **Backend Developer:** [Jenefer Yago]
- **Database Design:** [Mahammad Rustamov]
- **Team Members:** 5 total (Kanban team)

---

## Documentation

- **API Docs (Swagger UI):** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Trello Board:** [https://trello.com/invite/b/68e5694ffe5d33e3b3d92625/ATTI87d45e4d1d81d039df7f8e174aa1df0c51A5FB9B/agile-project-managemen-project]

---

## Roadmap

### ✅ Completed
- [x] Phase 1: Project Setup
- [x] Phase 2: Database Models  
- [x] Phase 3: Authentication System

### 🔄 In Progress
- [ ] Phase 4: Deals Management
- [ ] Phase 5: Business Profiles
- [ ] Phase 6: Location Features
- [ ] Phase 7: Frontend Integration

### Future Features
- [ ] Email verification
- [ ] Password reset
- [ ] User favorites
- [ ] Deal notifications
- [ ] Business analytics
- [ ] Admin panel
- [ ] Mobile app API

---

## License

This project is part of an academic course (Agile Project Management) at WSB University.

---

## Contributing

This is a course project. For team members:

1. Create a new branch for your feature
2. Make your changes
3. Test thoroughly
4. Create a pull request
5. Wait for code review

---

## Support

For issues or questions:
- Create an issue in GitHub
- Contact the project team
- Check the documentation

---

## Academic Context

**University:** WSB University in Dąbrowa Górnicza  
**Program:** Master's in Data Science  
**Course:** Agile Project Management  
**Professor:** Prof. Dawid Jurczyński

---

**Last Updated:** November 23, 2025  
**Version:** 0.3.0 (Phase 3 Complete)
