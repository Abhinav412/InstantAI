# LangGraph Chatbot (Local)

This project wraps your existing LangGraph pipeline (`test.py`) with a small FastAPI backend and a React + Vite frontend chat UI.

Structure
- backend/: FastAPI server that imports `test.py` and exposes `/chat` to run the pipeline.
- frontend/: Vite + React chat UI that calls `http://localhost:8000/chat`.

Quick start (Windows PowerShell)

1. Backend: create and activate the virtualenv (if you haven't already)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
```

2. Run backend

```powershell
uvicorn backend.main:app --reload --port 8000
```

3. Frontend

```powershell
cd frontend
npm install
npm run dev
```

You should now have a frontend at `http://localhost:5173` and backend at `http://localhost:8000`.

Notes
- The backend imports and calls `test.app.invoke(...)`. Make sure `test.py` is compatible with being imported (no top-level side-effects that conflict).
- For production you should not import the pipeline directly; instead package it as a module or run it as a worker process.
- CORS is wide open for local dev; restrict in production.

Crawler notes
- This project includes a simple crawler using Selenium + BeautifulSoup in `backend/crawler.py`.
- To enable Selenium crawling you need a browser driver (Chromedriver) on your PATH that matches your Chrome version. On Windows you can download Chromedriver and put it in a folder on your PATH, or use the ChromeDriverManager helper.
- If Selenium is not available, the crawler falls back to DuckDuckGo HTML search + requests + BeautifulSoup.

Install crawler deps in the backend venv:

```powershell
C:/LangGraph/.venv/Scripts/python.exe -m pip install -r backend/requirements.txt
```

If you plan to run Selenium headless, install a matching Chrome/Chromium and Chromedriver and ensure Chromedriver is accessible in PATH.
