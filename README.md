# Houston Jobs Hub

A local job board and business directory for Houston, Texas. This platform helps local businesses post job openings while creating high-quality backlinks and improving local SEO.

## 🌟 Features

- **Job Board**: Post and browse jobs in the Houston area
- **Business Directory**: Register your business for improved local visibility
- **Automated Directory Submission**: Submit your business to multiple local directories
- **SEO-optimized**: Structure designed to generate quality backlinks

## 🚀 Quick Start

### Prerequisites
- Node.js (v14 or higher)
- Python 3.8+ (for directory submitter)
- Git

### Installation

1. Clone the repository
```bash
git clone https://github.com/yourusername/houston-jobs-hub.git
cd houston-jobs-hub
```

2. Install dependencies
```bash
# Frontend dependencies
npm install

# Python dependencies for directory submitter
pip install -r requirements.txt
```

3. Set up environment variables
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Start the development server
```bash
npm run dev
```

5. Build for production
```bash
npm run build
```

## 📂 Project Structure

```
houston-jobs-hub/
├── public/              # Static files
├── src/                 # Source files
│   ├── components/      # React components
│   ├── pages/           # Page components
│   ├── styles/          # CSS files
│   ├── utils/           # Utility functions
│   └── App.js           # Main application component
├── scripts/             # Python scripts for directory submission
├── wireframes/          # Design wireframes
└── docs/                # Documentation
```

## 🔄 Deployment Workflow

This project uses a GitHub → Replit → Netlify workflow:

1. **GitHub**: Stores code and enables version control
2. **Replit**: Used for development and running the Python automation scripts
3. **Netlify**: Hosts the website with continuous deployment from GitHub

### Netlify Deployment

[![Deploy to Netlify](https://www.netlify.com/img/deploy/button.svg)](https://app.netlify.com/start/deploy?repository=https://github.com/yourusername/houston-jobs-hub)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👏 Acknowledgments

- Houston Chamber of Commerce
- Local businesses who contributed to testing
