# Finance tracker (React + Flask)

Local dev setup and run steps (Windows):

1. Create and activate venv (if not already):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install backend deps:

```powershell
.\.venv\Scripts\pip.exe install -r backend/requirements.txt
```

3. Initialize the database:

```powershell
.\.venv\Scripts\python.exe -m backend.scripts.init_db
```

4. Start the backend server:

```powershell
.\.venv\Scripts\python.exe -m backend.run
```

5. Frontend (install + start):

```bash
cd frontend
npm install
npm run dev
```

Environment notes:
- `SECRET_KEY` and `JWT_SECRET_KEY` can be set as environment variables for production.
- Backend defaults to a SQLite DB at `backend/instance/finance.db`.
