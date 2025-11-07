# 🚀 The Genesis Engine - Setup & Run Guide

## Prerequisites

- Python 3.10+
- Node.js 18+ and npm
- PostgreSQL (Tiger Cloud Database)
- Google Gemini API Key

---

## 📋 Initial Setup

### 1. Clone the Repository
```bash
git clone https://github.com/CheravGoyalShorthillsAI/Software_Architecture_Generator.git
cd Software_Architecture_Generator
```

### 2. Configure Environment Variables
```bash
# Copy the example env file
cp .env.example .env

# Edit .env with your actual credentials
nano .env  # or use your preferred editor
```

**Required Environment Variables in `.env`:**
```env
# Tiger Cloud Database Configuration
TIGER_SERVICE_ID=your_service_id
TIGER_DB_HOST=your_db_host
TIGER_DB_PORT=5432
TIGER_DB_NAME=your_db_name
TIGER_DB_USER=your_db_user
TIGER_DB_PASSWORD=your_db_password

# Gemini AI Configuration
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL_NAME=gemini-1.5-flash
GEMINI_EMBEDDING_MODEL=models/text-embedding-004
GEMINI_EMBEDDING_DIMENSION=768

# Optional Configuration
APP_ENV=development
DEBUG=True
API_HOST=0.0.0.0
API_PORT=8000
```

---

## 🐍 Backend Setup & Run

### Setup (First Time Only)

```bash
# Navigate to project root
cd Software_Architecture_Generator

# Create Python virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate  # On Windows

# Install backend dependencies
cd backend
pip install -r requirements.txt
```

### Run Backend Server

```bash
# Make sure you're in the project root and venv is activated
cd /path/to/Software_Architecture_Generator
source venv/bin/activate

# Run the FastAPI server
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Backend will be running at:** `http://localhost:8000`

**API Documentation:** `http://localhost:8000/docs`

---

## ⚛️ Frontend Setup & Run

### Setup (First Time Only)

```bash
# Navigate to frontend directory
cd Software_Architecture_Generator/frontend

# Install dependencies
npm install
```

### Run Frontend Development Server

```bash
# Navigate to frontend directory
cd /path/to/Software_Architecture_Generator/frontend

# Start the development server
npm run dev
```

**Frontend will be running at:** `http://localhost:3000`

---

## 🔥 Quick Start (Both Services)

### Terminal 1 - Backend
```bash
cd /path/to/Software_Architecture_Generator
source venv/bin/activate
cd backend
uvicorn app.main:app --reload --port 8000
```

### Terminal 2 - Frontend
```bash
cd /path/to/Software_Architecture_Generator/frontend
npm run dev
```

### Open in Browser
Navigate to: **http://localhost:3000**

---

## 🛠️ Common Commands

### Backend Commands

```bash
# Install new Python package
pip install package-name
pip freeze > requirements.txt

# Check if backend is running
curl http://localhost:8000/health

# View API documentation
open http://localhost:8000/docs
```

### Frontend Commands

```bash
# Install new npm package
npm install package-name

# Build for production
npm run build

# Preview production build
npm run preview

# Run linter
npm run lint
```

---

## 🔍 Troubleshooting

### Backend Issues

**Issue:** `ModuleNotFoundError: No module named 'X'`
```bash
source venv/bin/activate
pip install -r requirements.txt
```

**Issue:** Database connection error
- Check your `.env` file has correct Tiger Cloud credentials
- Ensure Tiger Cloud database is accessible
- Test connection: `psql -h $TIGER_DB_HOST -U $TIGER_DB_USER -d $TIGER_DB_NAME`

**Issue:** `pydantic` version conflicts
```bash
pip install pydantic-settings
```

### Frontend Issues

**Issue:** `node_modules` errors
```bash
rm -rf node_modules package-lock.json
npm install
```

**Issue:** Port 3000 already in use
```bash
# Kill process on port 3000
lsof -ti:3000 | xargs kill -9

# Or use a different port
npm run dev -- --port 3001
```

**Issue:** Vite build errors
```bash
npm run build --verbose
```

---

## 📊 Project Structure

```
Software_Architecture_Generator/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI application
│   │   ├── agents.py        # AI agents (Gemini)
│   │   ├── models.py        # Database models
│   │   ├── schemas.py       # Pydantic schemas
│   │   ├── crud.py          # Database operations
│   │   ├── database.py      # DB connection
│   │   └── config.py        # Configuration
│   ├── requirements.txt     # Python dependencies
│   └── README.md
├── frontend/
│   ├── src/
│   │   ├── App.tsx          # Main application
│   │   ├── components/      # React components
│   │   └── services/        # API client
│   ├── package.json         # Node dependencies
│   └── vite.config.ts       # Vite configuration
├── .env                     # Environment variables
└── README.md
```

---

## 🎯 Key Features

- **Multi-Agent Architecture Generation:** Architect, Systems Analyst, BizOps Analyst
- **LLM-Powered Diagrams:** Auto-generated Mermaid.js architecture diagrams
- **Hybrid Search:** Keyword (BM25) + Semantic (pgvector) search
- **Database Forks:** Zero-copy database forks for agent isolation
- **Real-Time Analysis:** Risk detection with severity ratings (1-10)
- **Project History:** Track and revisit generated architectures

---

## 🧪 Testing

### Test Backend API
```bash
# Health check
curl http://localhost:8000/health

# Create a project
curl -X POST http://localhost:8000/projects \
  -H "Content-Type: application/json" \
  -d '{"user_prompt": "Build a real-time chat application"}'

# Get project status
curl http://localhost:8000/projects/{project_id}/status
```

### Test Frontend
1. Open http://localhost:3000
2. Enter a project prompt
3. Click "Generate Architecture"
4. View the generated blueprint and analysis

---

## 📝 Notes

- Backend runs on port **8000**
- Frontend runs on port **3000**
- Make sure both are running for full functionality
- Frontend makes API calls to `http://localhost:8000`
- Database migrations are automatic on startup
- Logs are visible in the terminal

---

## 🤝 Collaboration Tips

### Sharing with Team Members

1. **Share this file** with team members
2. Ensure they have access to:
   - Tiger Cloud Database credentials
   - Gemini API key
3. They should create their own `.env` file (don't commit it!)
4. Run `git pull` to get latest changes

### Before Committing

```bash
# Check status
git status

# Add changes
git add .

# Commit with meaningful message
git commit -m "Description of changes"

# Pull latest changes
git pull origin main

# Push your changes
git push origin main
```

---

## 🆘 Support

For issues or questions:
- Check logs in terminal where services are running
- Review API docs at http://localhost:8000/docs
- Check browser console for frontend errors (F12)
- Ensure all environment variables are set correctly

---

**Happy Coding! 🚀**

