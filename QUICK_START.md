# ⚡ Quick Start Guide - The Genesis Engine

## 🚀 Run Backend & Frontend

### Option 1: Quick Commands (Copy & Paste)

**Terminal 1 - Backend:**
```bash
cd /path/to/Software_Architecture_Generator
source venv/bin/activate
cd backend
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd /path/to/Software_Architecture_Generator/frontend
npm run dev
```

**Open:** http://localhost:3000

---

### Option 2: First Time Setup

#### Backend Setup:
```bash
cd Software_Architecture_Generator
python3 -m venv venv
source venv/bin/activate
cd backend
pip install -r requirements.txt
```

#### Frontend Setup:
```bash
cd Software_Architecture_Generator/frontend
npm install
```

#### Configure `.env`:
```bash
cp .env.example .env
# Edit .env with your credentials
```

---

## 📍 URLs

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:3000 | Main application UI |
| Backend API | http://localhost:8000 | FastAPI server |
| API Docs | http://localhost:8000/docs | Swagger documentation |
| Health Check | http://localhost:8000/health | Backend status |

---

## 🔑 Required Environment Variables

Create a `.env` file in the project root:

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
```

---

## 🛠️ Common Issues

| Problem | Solution |
|---------|----------|
| Backend won't start | `source venv/bin/activate` then `pip install -r requirements.txt` |
| Frontend errors | `rm -rf node_modules && npm install` |
| Port 8000 in use | `lsof -ti:8000 \| xargs kill -9` |
| Port 3000 in use | `lsof -ti:3000 \| xargs kill -9` |
| Database error | Check `.env` credentials |

---

## ✅ Verify Everything is Working

```bash
# Test backend
curl http://localhost:8000/health

# Should return: {"status": "ok"}
```

Open http://localhost:3000 and enter a prompt like:
```
Build a real-time video streaming platform with CDN, authentication, and analytics
```

---

**Need more details?** See [SETUP_AND_RUN.md](./SETUP_AND_RUN.md)

