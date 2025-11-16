# Backend (pii scanner) — quick start

This folder contains the backend FastAPI app used by the project.

Requirements
- Python 3.10+ recommended

Install dependencies

From the repository root (Windows cmd):

```cmd
cd /d C:\Users\simpl\Desktop\capstone\backend
python -m pip install -r requirements.txt
```

Run tests

```cmd
cd /d C:\Users\simpl\Desktop\capstone\backend
python -m pytest -q
```

Run the server (development)

```cmd
cd /d C:\Users\simpl\Desktop\capstone\backend
python run_server.py
```

Notes
- The `run_server.py` file launches uvicorn for local development. Disable `reload=True` for production.
- I pinned `setuptools<81` in `requirements.txt` to reduce a deprecation warning emitted by the `tika` package. If you update `tika` or `setuptools` later, you can remove or change this pin.
- Frontend is in the top-level `frontend/` folder and contains a built `build/` directory for static hosting.
