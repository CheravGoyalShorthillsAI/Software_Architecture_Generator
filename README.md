# The Genesis Engine

[Add your project description here]

## Setup

Run the setup script:
```bash
chmod +x setup.sh
./setup.sh
```

Then activate the virtual environment:
```bash
source venv/bin/activate
```

## Project Structure

- `backend/` - Python backend application
- `frontend/` - Node.js/React frontend application

## Environment Variables

Copy `.env.example` to `.env` and fill in your configuration:

```bash
cp .env.example .env
```

Required environment variables:
- `TIGER_SERVICE_ID` - Tiger Cloud Database Service ID
- `TIGER_DB_HOST` - Tiger Cloud Database Host
- `TIGER_DB_PORT` - Tiger Cloud Database Port
- `TIGER_DB_NAME` - Tiger Cloud Database Name
- `TIGER_DB_USER` - Tiger Cloud Database User
- `TIGER_DB_PASSWORD` - Tiger Cloud Database Password
- `GEMINI_API_KEY` - Gemini AI API Key

## Getting Started

1. Set up your development environment by running the setup script
2. Activate the virtual environment
3. Configure your `.env` file with actual values
4. Navigate to either `backend/` or `frontend/` to start development

## Development

### Backend (Python)
```bash
cd backend
# Add backend-specific setup instructions here
```

### Frontend (Node.js/React)
```bash
cd frontend
# Add frontend-specific setup instructions here
```
