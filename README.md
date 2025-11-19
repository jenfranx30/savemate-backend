# SaveMate Backend

**Node.js/Express API for local deals and discounts platform**

##  Tech Stack

- Node.js 18+
- Express.js 4.x
- MongoDB Atlas
- Mongoose 7.x
- JWT Authentication
- Cloudinary (Image storage)
- bcryptjs (Password hashing)

##  Installation

### Prerequisites
- Node.js 18+ installed
- MongoDB Atlas account
- Cloudinary account (free tier)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/jenfranx30/savemate-backend.git
cd savemate-backend
```

2. Install dependencies:
```bash
npm install
```

3. Create `.env` file in root (see `.env.example` for template):
```env
NODE_ENV=development
PORT=5000
MONGODB_URI=your_mongodb_connection_string
JWT_SECRET=your_super_secret_key_min_32_chars
JWT_REFRESH_SECRET=your_refresh_secret_key
JWT_EXPIRE=7d
JWT_REFRESH_EXPIRE=30d
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
FRONTEND_URL=http://localhost:3000
```

4. Start development server:
```bash
npm run dev
```

Server will run at http://localhost:5000

##  Project Structure

```
savemate-backend/
├── config/
│   ├── database.js         # MongoDB connection
│   └── cloudinary.js       # Cloudinary config
├── models/
│   ├── User.js             # User schema
│   ├── Deal.js             # Deal schema
│   └── Business.js         # Business schema
├── controllers/
│   ├── authController.js   # Authentication logic
│   ├── userController.js   # User operations
│   ├── dealController.js   # Deal operations
│   └── businessController.js # Business operations
├── routes/
│   ├── auth.js             # Auth routes
│   ├── users.js            # User routes
│   ├── deals.js            # Deal routes
│   └── business.js         # Business routes
├── middleware/
│   ├── auth.js             # JWT authentication
│   └── error.js            # Error handling
├── utils/
│   └── generateToken.js    # JWT token generation
├── server.js               # Entry point
├── .env                    # Environment variables (not committed)
├── .env.example            # Template for .env
├── .gitignore
├── package.json
└── README.md
```

##  Available Scripts

- `npm start` - Start production server
- `npm run dev` - Start development server with nodemon
- `npm test` - Run tests (to be implemented)

##  API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `POST /api/auth/refresh` - Refresh access token

### Users
- `GET /api/users/profile` - Get user profile
- `PUT /api/users/profile` - Update user profile
- `POST /api/users/favorites/:dealId` - Save deal to favorites
- `DELETE /api/users/favorites/:dealId` - Remove from favorites
- `GET /api/users/favorites` - Get user's favorite deals

### Deals
- `GET /api/deals` - Get all deals (with pagination)
- `GET /api/deals/:id` - Get single deal
- `POST /api/deals` - Create deal (business only)
- `PUT /api/deals/:id` - Update deal (business only)
- `DELETE /api/deals/:id` - Delete deal (business only)
- `GET /api/deals/search` - Search deals

### Business
- `POST /api/business/register` - Register business
- `GET /api/business/:id` - Get business details
- `PUT /api/business/:id` - Update business
- `GET /api/business/:id/deals` - Get business deals

**Full API Documentation:** Coming in Week 2

##  Environment Variables

Create a `.env` file based on `.env.example`:

```env
# Server Configuration
NODE_ENV=development
PORT=5000

# Database
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/savemate

# JWT Secrets (Generate random 32+ character strings)
JWT_SECRET=your_super_secret_key_minimum_32_characters_long
JWT_REFRESH_SECRET=your_refresh_secret_also_32_chars_minimum

# JWT Expiration
JWT_EXPIRE=7d
JWT_REFRESH_EXPIRE=30d

# Cloudinary Configuration
CLOUDINARY_CLOUD_NAME=your_cloudinary_cloud_name
CLOUDINARY_API_KEY=your_cloudinary_api_key
CLOUDINARY_API_SECRET=your_cloudinary_api_secret

# Frontend URL (for CORS)
FRONTEND_URL=http://localhost:3000
```

**Security Notes:**
- Never commit `.env` file to Git
- Use strong, random secrets (32+ characters)
- Rotate secrets regularly in production

## Related Repositories

- **Frontend App:** [savemate-frontend](https://github.com/jenfranx30/savemate-frontend)
- **Documentation:** [savemate-docs](https://github.com/jenfranx30/savemate-docs)


## Database Schema

**Collections:**
- `users` - User accounts (regular users and businesses)
- `deals` - Deal/discount listings
- `businesses` - Business profiles
- `categories` - Deal categories

**Full schema documentation:** See `savemate-docs` repository

## Testing

```bash
# Install dependencies
npm install

# Run tests (to be implemented in Week 6)
npm test

# Test API endpoints with:
# - Postman collection (coming soon)
# - curl commands
# - REST Client extension
```

## Troubleshooting

**Port 5000 already in use:**
```bash
# Change PORT in .env file
PORT=5001
```

**MongoDB connection error:**
- Check MONGODB_URI in .env
- Verify IP whitelist in MongoDB Atlas (0.0.0.0/0 for development)
- Check database user credentials

**Module not found:**
```bash
rm -rf node_modules package-lock.json
npm install
```

## License

Academic project for WSB University - Winter 2025-2026

---

**Status:**  In Development  
**Last Updated:** November 26, 2025
