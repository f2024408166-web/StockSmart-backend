# StockSmart Backend

FastAPI backend for the StockSmart Inventory Management System.

## Local Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env       # Fill in your Supabase DATABASE_URL and SECRET_KEY
uvicorn main:app --reload
```

API Docs: http://localhost:8000/docs

## Vercel Deployment

See the deployment guidance document included in this project.
