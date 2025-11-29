# SaveMate Backend API

**Modern Python/FastAPI backend for SaveMate - Local Deals Platform**

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)](https://fastapi.tiangolo.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-7.0%2B-brightgreen.svg)](https://www.mongodb.com/)

---

A comprehensive local deals and discounts platform backend built with FastAPI and MongoDB. SaveMate connects consumers with local businesses offering deals and discounts in Poland.

## Project Overview

SaveMate is a full-stack web application that helps users discover and save money on local deals in their area. The backend API provides complete functionality for authentication, deal management, business profiles, user favorites, and review systems.

 
**Project Management:** Trello

---

## ✅ Development Status

### Phase 1: Project Setup ✅ (Complete)
- ✅ Project structure created
- ✅ Git repository initialized
- ✅ MongoDB Atlas configured
- ✅ Environment setup

### Phase 2: Database Models ✅ (Complete)
- ✅ User model with Beanie ODM
- ✅ Deal model with comprehensive fields
- ✅ Business model with ratings
- ✅ Category model
- ✅ Favorite model (user-deal relationship)
- ✅ Review model with ratings
- ✅ MongoDB connection established

### Phase 3: Authentication System ✅ (Complete)
- ✅ User registration endpoint
- ✅ Login with email/username support
- ✅ JWT token authentication (access + refresh)
- ✅ Token refresh mechanism
- ✅ Password hashing with bcrypt
- ✅ Pydantic validation schemas
- ✅ Swagger UI documentation

### Phase 4: Deals Management ✅ (Complete)
- ✅ Complete CRUD operations for deals
- ✅ Advanced filtering (category, city, price, discount)
- ✅ Full-text search functionality
- ✅ Pagination and sorting
- ✅ 10 deal categories
- ✅ Location tracking with coordinates
- ✅ View and save counters
- ✅ Deal expiration handling
- ✅ Status tracking

### Phase 5: Business, Favorites & Reviews ✅ (Complete)
- ✅ Business profile management (7 endpoints)
- ✅ User favorites system (4 endpoints)
- ✅ Reviews and ratings (5 endpoints)
- ✅ Business ratings calculation
- ✅ Operating hours support
- ✅ Duplicate review prevention
- ✅ Helpful votes system

### Phase 6: Coming Soon 🔄
- 🔄 API Integration (Polish APIs)
- 🔄 Advanced search with geolocation
- 🔄 Email notifications
- 🔄 Admin dashboard

---
## 🗂️ Category Management

### Overview
Categories organize deals into logical groups (Food and Dining, Shopping, Entertainment, etc.).

### Features
- ✅ Hierarchical categories (parent-child relationships)
- ✅ Featured categories for homepage
- ✅ Category statistics and analytics
- ✅ Search and filtering
- ✅ Admin-only management
- ✅ Public browsing

### API Endpoints

#### Public Endpoints (No Authentication)
```
GET  /api/v1/categories/              - List all categories with pagination
GET  /api/v1/categories/featured      - Get featured categories
GET  /api/v1/categories/slug/{slug}   - Get category by slug
GET  /api/v1/categories/{id}          - Get category by ID
GET  /api/v1/categories/stats/overview - Get statistics
```

#### Admin Endpoints (Authentication Required)
```
POST   /api/v1/categories/     - Create new category
PUT    /api/v1/categories/{id} - Update category
DELETE /api/v1/categories/{id} - Delete category
```

### Admin Management

#### Make a User Admin
```bash
python scripts/make_admin.py
# Select option 1
# Enter user email
```

#### List All Admins
```bash
python scripts/make_admin.py
# Select option 3
```

### Sample Categories
```json
{
  "name": "Food & Dining",
  "slug": "food-dining",
  "description": "Restaurants, cafes, and food delivery services",
  "icon": "🍔",
  "color": "#EF4444",
  "is_featured": true
}
```

### Testing
```bash
# Run category tests
pytest app/tests/test_categories.py -v

# Run with coverage
pytest app/tests/test_categories.py --cov=app.models.category --cov=app.schemas.category_schema --cov-report=term-missing
```

### Coverage
- Model: 83%
- Schemas: 96%
- Overall: 83%+


## 🛠️ Tech Stack

### Backend Framework
- **FastAPI 0.104+** - Modern, fast web framework
- **Python 3.8+** - Programming language
- **Uvicorn** - ASGI server

### Database
- **MongoDB Atlas** - Cloud database
- **Beanie ODM** - Object Document Mapper
- **Motor** - Async MongoDB driver

### Authentication and Security
- **JWT (JSON Web Tokens)** - Stateless authentication
- **bcrypt 4.1.2** - Password hashing
- **python-jose** - JWT handling

### Validation and Serialization
- **Pydantic 2.5+** - Data validation
- **Pydantic Settings** - Configuration management

### Development Tools
- **Git** - Version control
- **Swagger UI** - Auto-generated API docs
- **ReDoc** - Alternative API documentation

---

##  Installation and Setup

### Prerequisites

- Python 3.8 or higher
- MongoDB Atlas account (or local MongoDB)
- Git
- pip (Python package manager)

### Step 1: Clone the Repository

```bash
git clone https://github.com/jenfranx30/savemate-backend.git
cd savemate-backend
```

### Step 2: Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**Key Dependencies:**
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
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
DATABASE_NAME=savemate

# JWT Configuration
JWT_SECRET=your-super-secret-key-minimum-32-characters-long-change-this
JWT_REFRESH_SECRET=your-refresh-secret-also-minimum-32-characters-change-this
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Application Settings
PROJECT_NAME=SaveMate API
DEBUG=True
API_V1_PREFIX=/api/v1
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# Server Configuration
HOST=127.0.0.1
PORT=8000
```

**⚠️ Important:** Never commit `.env` to Git! It's already in `.gitignore`.

### Step 5: Run the Server

```bash
uvicorn app.main:app --reload
```

**Expected output:**
```
🚀 Starting SaveMate API...
✅ Connected to MongoDB database: savemate
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Step 6: Access API Documentation

Open your browser and navigate to:

**Swagger UI:** `http://localhost:8000/docs`  
**ReDoc:** `http://localhost:8000/redoc`

---

## 🔐 API Endpoints

### Authentication (3 endpoints)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/auth/register` | Register new user | No |
| POST | `/api/v1/auth/login` | Login user | No |
| POST | `/api/v1/auth/refresh` | Refresh access token | No |

### Deals (6 endpoints)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/deals/` | Create deal | Yes |
| GET | `/api/v1/deals/` | Get all deals (with filters) | No |
| GET | `/api/v1/deals/{id}` | Get single deal | No |
| PUT | `/api/v1/deals/{id}` | Update deal | Yes |
| DELETE | `/api/v1/deals/{id}` | Delete deal | Yes |
| GET | `/api/v1/deals/category/{category}` | Get deals by category | No |

### Businesses (7 endpoints)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/businesses/` | Create business | Yes |
| GET | `/api/v1/businesses/` | Get all businesses | No |
| GET | `/api/v1/businesses/{id}` | Get single business | No |
| PUT | `/api/v1/businesses/{id}` | Update business | Yes |
| DELETE | `/api/v1/businesses/{id}` | Delete business | Yes |
| GET | `/api/v1/businesses/owner/{user_id}` | Get user's businesses | No |
| GET | `/api/v1/businesses/{id}/deals` | Get business deals | No |

### Favorites (4 endpoints)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/favorites/` | Add to favorites | Yes |
| DELETE | `/api/v1/favorites/{deal_id}` | Remove from favorites | Yes |
| GET | `/api/v1/favorites/` | Get user favorites | Yes |
| GET | `/api/v1/favorites/check/{deal_id}` | Check if favorited | Yes |

### Reviews (5 endpoints)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/reviews/` | Create review | Yes |
| GET | `/api/v1/reviews/deal/{deal_id}` | Get deal reviews | No |
| GET | `/api/v1/reviews/user/{user_id}` | Get user reviews | No |
| PUT | `/api/v1/reviews/{id}` | Update review | Yes |
| POST | `/api/v1/reviews/{id}/helpful` | Mark as helpful | Yes |

**Total: 25 Endpoints**

---

## 📁 Project Structure

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
│   │   ├── user.py                  # User document model
│   │   ├── deal.py                  # Deal document model
│   │   ├── business.py              # Business document model
│   │   ├── category.py              # Category document model
│   │   ├── favorite.py              # Favorite document model
│   │   └── review.py                # Review document model
│   │
│   ├── schemas/                     # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── auth_schema.py           # Authentication schemas
│   │   ├── deal_schema.py           # Deal schemas
│   │   ├── business_schema.py       # Business schemas
│   │   ├── favorite_schema.py       # Favorite schemas
│   │   └── review_schema.py         # Review schemas
│   │
│   ├── api/                         # API routes
│   │   ├── __init__.py
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── auth.py              # Authentication endpoints
│   │       ├── deals.py             # Deal endpoints
│   │       ├── businesses.py        # Business endpoints
│   │       ├── favorites.py         # Favorite endpoints
│   │       └── reviews.py           # Review endpoints
│   │
│   ├── db/                          # Database configuration
│   │   ├── __init__.py
│   │   └── database.py              # MongoDB connection
│   │
│   └── config.py                    # Application configuration
│
├── .env                             # Environment variables (not in Git)
├── .gitignore                       # Git ignore file
├── requirements.txt                 # Python dependencies
└── README.md                        # This file
```

---

## 🧪 Testing Examples

### 1. Register a New User

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "johndoe",
    "password": "SecurePass123!",
    "full_name": "John Doe",
    "is_business_owner": false
  }'
```

### 2. Create a Deal

```bash
curl -X POST "http://localhost:8000/api/v1/deals/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "50% Off Large Pizza",
    "description": "Get half off any large pizza with 3 or more toppings.",
    "original_price": 39.99,
    "discounted_price": 19.99,
    "category": "food",
    "business_name": "Mario'\''s Pizzeria",
    "location": {
      "address": "ul. Marszałkowska 123",
      "city": "Warsaw",
      "postal_code": "00-001",
      "country": "Poland"
    },
    "end_date": "2025-12-31T23:59:59"
  }'
```

### 3. Search for Deals

```bash
# Get all food deals in Warsaw
curl "http://localhost:8000/api/v1/deals/?category=food&city=Warsaw"

# Get deals with 50%+ discount
curl "http://localhost:8000/api/v1/deals/?min_discount=50"

# Search for pizza
curl "http://localhost:8000/api/v1/deals/?search=pizza"
```

---

## Database Schema

### Collections

1. **users** - User accounts
2. **deals** - Deal listings
3. **businesses** - Business profiles
4. **categories** - Deal categories
5. **favorites** - User favorite deals
6. **reviews** - Deal reviews and ratings

See `SaveMate_Database_Schema.md` for complete schema documentation.

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
- **CORS Configuration:** Configurable allowed origins
- **Environment Variables:** Sensitive data in `.env`

---

## Troubleshooting

### Server Won't Start

**Check port availability:**
```bash
# Windows
netstat -ano | findstr :8000

# macOS/Linux
lsof -i :8000
```

### MongoDB Connection Error

**Solutions:**
- Verify `MONGODB_URL` in `.env`
- Check MongoDB Atlas IP whitelist
- Ensure network connectivity
- Test connection string separately

### Package Installation Errors

**Solutions:**
```bash
# Upgrade pip
python -m pip install --upgrade pip

# Clear cache and reinstall
pip cache purge
pip install -r requirements.txt
```

### Bcrypt Error

**Solution:**
```bash
pip uninstall -y passlib bcrypt
pip install passlib==1.7.4 bcrypt==4.1.2
```

---

## 🌍 Deployment

### MongoDB Atlas Setup

1. Create account at https://mongodb.com/cloud/atlas
2. Create a cluster (Free tier available)
3. Add database user with strong password
4. Whitelist IP address (0.0.0.0/0 for development)
5. Get connection string
6. Update `MONGODB_URL` in `.env`

### Production Considerations

- ✅ Use strong JWT secrets (32+ characters)
- ✅ Enable HTTPS
- ✅ Set proper CORS origins
- ✅ Use environment-specific configurations
- ✅ Implement rate limiting
- ✅ Add logging and monitoring
- ✅ Regular database backups
- ✅ Error tracking (Sentry)
- ✅ Performance monitoring

---

## 👥 Team and Contributors

- **Project Lead:** Rustam Islamov
- **Backend Developer:** Jenefer Yago
- **Database Design:** Mahammad Rustamov
- **Team Members:** Rustam Yariyev and Sadig Shikhaliyev
- **Methodology:** Kanban (Trello)

---

## 📚 Documentation

- **API Docs (Swagger UI):** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Database Schema:** See `SaveMate_Database_Schema.md`
- **API Documentation:** See `SaveMate_API_Documentation.md`
- **Trello Board:** [https://trello.com/invite/b/68e5694ffe5d33e3b3d92625/ATTI87d45e4d1d81d039df7f8e174aa1df0c51A5FB9B/agile-project-managemen-project]

---

## 🎯 Roadmap

### ✅ Completed (Phases 1-5)
- [x] Project Setup
- [x] Database Models  
- [x] Authentication System
- [x] Deals Management
- [x] Business Profiles
- [x] Favorites System
- [x] Reviews & Ratings

### 🔄 In Progress (Phase 6)
- [ ] Polish API Integration
  - [ ] Google Places API
  - [ ] Allegro API
  - [ ] OpenStreetMap
  - [ ] GUS API
- [ ] Advanced Geolocation Search
- [ ] Email Notifications
- [ ] Admin Dashboard

### 🔮 Future Features (Phase 7+)
- [ ] Frontend (React + Vite + Tailwind)
- [ ] Mobile App API
- [ ] Push Notifications
- [ ] Social Media Integration
- [ ] Analytics Dashboard
- [ ] Multi-language Support
- [ ] Payment Integration
- [ ] Deal Redemption QR Codes
- [ ] Business Verification System

---

## 📄 License

This project is part of an academic course (Agile Project Management) at WSB University.

---

## 📞 Support

For issues or questions:
- Create an issue in GitHub
- Contact the project team
- Check the documentation
- Review Swagger UI examples

---

## Academic Context

**University:** WSB University in Dąbrowa Górnicza  
**Program:** Master's in Data Science 
**Course:** Agile Project Management  
**Professor:** Prof. Dawid Jurczyński 
**Timeline:** November 2025 - January 2026  
**Project Type:** Team Project (5 members)  
**Methodology:** Kanban

---

## 📈 Project Statistics

- **Total Endpoints:** 25
- **Total Models:** 6
- **Total Lines of Code:** ~5,000+
- **Test Coverage:** Coming soon
- **API Response Time:** <100ms average
- **Database Collections:** 6
- **Authentication:** JWT-based
- **Documentation:** Auto-generated (Swagger)

---

**Last Updated:** November 24, 2025  
**Version:** 1.0.0 (Phase 5 Complete)  
**Status:** ✅ Active Development

---

For detailed API documentation, see [SaveMate_API_Documentation.md](SaveMate_API_Documentation.md)
