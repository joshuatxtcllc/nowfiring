/**
 * Houston Jobs Hub - Basic Express Server
 * This provides a simple server for development
 * In production, you can use Netlify for hosting static files
 */

const express = require('express');
const path = require('path');
const cors = require('cors');
require('dotenv').config();

// Initialize Express app
const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Serve static files from public directory
app.use(express.static(path.join(__dirname, 'public')));

// Routes
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'index.html'));
});

// Sample API endpoint for future implementation
app.get('/api/jobs', (req, res) => {
  // This would normally fetch from a database
  const sampleJobs = [
    {
      id: 1,
      title: 'Senior Web Developer',
      company: 'Example Company',
      location: 'Downtown Houston',
      type: 'Full-time',
      salary: '$90,000 - $120,000',
      posted: '2 days ago',
      description: 'Join our team of passionate developers...'
    },
    {
      id: 2,
      title: 'Marketing Specialist',
      company: 'Houston Marketing Group',
      location: 'Midtown, Houston',
      type: 'Full-time',
      salary: '$60,000 - $75,000',
      posted: '1 day ago',
      description: 'We are looking for a creative marketing specialist...'
    }
  ];
  
  res.json(sampleJobs);
});

// Sample API endpoint for businesses
app.get('/api/businesses', (req, res) => {
  // This would normally fetch from a database
  const sampleBusinesses = [
    {
      id: 1,
      name: 'Example Business',
      category: 'Technology',
      location: 'Midtown, Houston',
      description: 'A leading technology company providing innovative solutions...'
    },
    {
      id: 2,
      name: 'Houston Services Co.',
      category: 'Professional Services',
      location: 'Downtown Houston',
      description: 'Professional services for Houston businesses...'
    }
  ];
  
  res.json(sampleBusinesses);
});

// Start server
app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
