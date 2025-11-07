# 🏗️ The Genesis Engine

**AI-Powered Software Architecture Generator using Parallel Agents & Database Forks**

The Genesis Engine is an innovative architecture design tool that leverages multiple AI agents working in parallel with isolated database forks to generate comprehensive microservices architecture blueprints with detailed analysis.

## ✨ Features

- 🤖 **3 AI Agents Working in Parallel**
  - **Architect Agent**: Generates microservices architecture blueprints
  - **Systems Analyst**: Analyzes technical risks (security, performance, scalability)
  - **BizOps Analyst**: Analyzes business risks (cost, operations, compliance)

- 🗄️ **Isolated Database Forks** (Tiger Cloud)
  - Fast, zero-copy database forks for each blueprint
  - Complete data isolation between analyses
  - 110k+ IOPS performance

- 🔍 **Hybrid Search**
  - Keyword search (PostgreSQL full-text)
  - Semantic search (pgvector embeddings)
  - Search across all project analyses

- 🎨 **Architecture Diagrams**
  - AI-generated Mermaid.js diagrams
  - Domain-specific, production-grade visualizations
  - 20-30+ node detailed diagrams
  - Download as SVG or Mermaid code

- 📚 **Project History**
  - View all generated projects
  - Filter by status
  - Delete projects

- 📄 **Markdown Descriptions**
  - Well-formatted architecture descriptions
  - Sections with headings, lists, and emphasis
  - Easy to read and understand

---

## 📋 Prerequisites

- **Python 3.10+**
- **Node.js 18+** and npm
- **PostgreSQL** (Tiger Cloud Database recommended)
- **Google Gemini API Key**

---

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/CheravGoyalShorthillsAI/Software_Architecture_Generator.git
cd Software_Architecture_Generator
```

### 2. Configure Environment Variables
```bash
cp .env.example .env
# Edit .env with your actual credentials
```

**Required `.env` variables:**
```env
# Tiger Cloud Database
TIGER_SERVICE_ID=your_service_id
TIGER_DB_HOST=your_host
TIGER_DB_PORT=5432
TIGER_DB_NAME=your_db_name
TIGER_DB_USER=your_user
TIGER_DB_PASSWORD=your_password

# Gemini AI
GEMINI_API_KEY=your_api_key
GEMINI_MODEL_NAME=gemini-1.5-flash
GEMINI_EMBEDDING_MODEL=models/text-embedding-004
GEMINI_EMBEDDING_DIMENSION=768
```

### 3. Setup Backend
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate  # On Windows

# Install dependencies
cd backend
pip install -r requirements.txt
```

### 4. Setup Frontend
```bash
cd frontend
npm install
```

### 5. Run Both Services

**Terminal 1 - Backend:**
```bash
cd Software_Architecture_Generator
source venv/bin/activate
cd backend
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd Software_Architecture_Generator/frontend
npm run dev
```

### 6. Access the Application
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

---

## 🎯 Usage

1. Open http://localhost:3000
2. Enter your project prompt, e.g.:
   ```
   Build a real-time collaborative task management application with team workspaces, 
   file attachments, and comprehensive authentication
   ```
3. Click "Generate Architecture"
4. Wait for analysis to complete (usually 30-60 seconds)
5. View the generated:
   - Microservices architecture blueprint
   - Architecture diagram
   - Systems analyst findings
   - BizOps analyst findings
   - Pros and cons analysis

---

## 📁 Project Structure

```
Software_Architecture_Generator/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── main.py            # API endpoints & orchestration
│   │   ├── agents.py          # AI agent implementations
│   │   ├── models.py          # Database models
│   │   ├── schemas.py         # Pydantic schemas
│   │   ├── crud.py            # Database operations
│   │   ├── database.py        # Database configuration
│   │   └── config.py          # Settings & environment variables
│   └── requirements.txt       # Python dependencies
│
├── frontend/                  # React + Vite frontend
│   ├── src/
│   │   ├── App.tsx           # Main application component
│   │   ├── components/       # Reusable UI components
│   │   │   ├── ArchitectureCard.tsx
│   │   │   ├── ArchitectureDiagram.tsx
│   │   │   ├── ProjectHistory.tsx
│   │   │   ├── SearchBar.tsx
│   │   │   ├── Spinner.tsx
│   │   │   └── ResultsDisplay.tsx
│   │   └── services/
│   │       └── api.ts        # API service layer
│   ├── package.json          # Node dependencies
│   └── tailwind.config.js    # Tailwind CSS config
│
├── .env                       # Environment variables (create this)
├── .env.example              # Environment variables template
└── README.md                 # This file
```

---

## 🛠️ API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API information |
| GET | `/health` | Health check |
| POST | `/projects` | Create new project |
| GET | `/projects` | List all projects |
| GET | `/projects/{id}` | Get project details |
| GET | `/projects/{id}/status` | Check project status |
| POST | `/projects/{id}/search` | Search analyses |
| DELETE | `/projects/{id}` | Delete project |

---

## 🔧 Common Commands

### Backend
```bash
# Activate virtual environment
source venv/bin/activate

# Install new package
pip install package-name
pip freeze > requirements.txt

# Run backend
cd backend
uvicorn app.main:app --reload --port 8000

# Check health
curl http://localhost:8000/health
```

### Frontend
```bash
# Install new package
npm install package-name

# Run development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| Backend won't start | Check if venv is activated: `source venv/bin/activate` |
| Missing Python packages | `pip install -r backend/requirements.txt` |
| Frontend errors | `cd frontend && rm -rf node_modules && npm install` |
| Port 8000 in use | `lsof -ti:8000 \| xargs kill -9` |
| Port 3000 in use | `lsof -ti:3000 \| xargs kill -9` |
| Database connection error | Verify `.env` credentials |
| Pydantic validation error | Check `.env` for missing required fields |
| Mermaid diagram errors | Regenerate project (older projects may have syntax issues) |

---

## 🏗️ Architecture Overview

### Multi-Agent System
The Genesis Engine uses three specialized AI agents powered by Google Gemini:

1. **Architect Agent**
   - Generates microservices architecture blueprints
   - Includes detailed descriptions with Markdown formatting
   - Provides pros and cons analysis

2. **Systems Analyst Agent** (runs in parallel)
   - Analyzes technical aspects
   - Identifies security vulnerabilities
   - Assesses performance and scalability risks
   - Severity rating (1-10 scale)

3. **BizOps Analyst Agent** (runs in parallel)
   - Analyzes business operations
   - Calculates cost implications
   - Evaluates team structure needs
   - Assesses compliance requirements

### Database Forks (Tiger Cloud)
- Each blueprint is analyzed in an isolated database fork
- Zero-copy forks created using Tiger CLI
- Parallel processing without data conflicts
- Fast fork technology (< 1 second creation)

### Search System
- **Hybrid Search**: Combines keyword (BM25) and semantic search (vector embeddings)
- **pgvector**: Stores embeddings for semantic similarity
- **PostgreSQL Full-Text Search**: Keyword matching
- Search across all analyses for a project

---

## 🎨 Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Primary database (Tiger Cloud)
- **pgvector** - Vector similarity search
- **SQLAlchemy** - ORM
- **Google Gemini AI** - LLM for agents and embeddings
- **Pydantic** - Data validation

### Frontend
- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Axios** - HTTP client
- **Mermaid.js** - Diagram rendering

---

## 📝 Environment Variables Reference

```env
# Tiger Cloud Database Configuration
TIGER_SERVICE_ID=your_service_id          # Required: Tiger service ID for forking
TIGER_DB_HOST=your_db_host                # Required: Database hostname
TIGER_DB_PORT=5432                        # Required: Database port
TIGER_DB_NAME=your_db_name                # Required: Database name
TIGER_DB_USER=your_db_user                # Required: Database username
TIGER_DB_PASSWORD=your_db_password        # Required: Database password

# Gemini AI Configuration
GEMINI_API_KEY=your_gemini_api_key        # Required: Google Gemini API key
GEMINI_MODEL_NAME=gemini-1.5-flash        # Optional: Model for generation
GEMINI_EMBEDDING_MODEL=models/text-embedding-004  # Optional: Embedding model
GEMINI_EMBEDDING_DIMENSION=768            # Optional: Embedding dimensions

# Optional Application Configuration
APP_ENV=development                       # Optional: Environment mode
DEBUG=True                               # Optional: Debug mode
API_HOST=0.0.0.0                        # Optional: API host
API_PORT=8000                           # Optional: API port
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

## 📄 License

[Add your license information here]

---

## 🙏 Acknowledgments

- **Tiger Cloud** - For the fast database forking technology
- **Google Gemini AI** - For powering the AI agents
- **Agentic Postgres Hackathon** - For the inspiration

---

## 📞 Support

For issues and questions:
- Open an issue on GitHub
- Check the [API Documentation](http://localhost:8000/docs) when backend is running

---

**Built with ❤️ for the Agentic Postgres Hackathon**
