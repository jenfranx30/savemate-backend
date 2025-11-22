require('dotenv').config();
const express = require('express');
const cors = require('cors');
const helmet = require('helmet');

const app = express();
const PORT = process.env.PORT || 5000;

// Middleware
app.use(helmet());
app.use(cors());
app.use(express.json());

// Root route - so localhost:5000 shows something
app.get('/', (req, res) => {
  res.send('SaveMate backend is running ✅');
});

// Health check route
app.get('/api/health', (req, res) => {
  res.json({
    status: 'ok',
    message: 'SaveMate API is running',
    timestamp: new Date().toISOString()
  });
});

// Start server
app.listen(PORT, () => {
  console.log(`🚀 Server running on http://localhost:${PORT}`);
  console.log(`📍 Health check: http://localhost:${PORT}/api/health`);
});
