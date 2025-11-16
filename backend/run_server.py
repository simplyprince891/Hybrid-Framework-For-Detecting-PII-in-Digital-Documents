"""Small launcher to run the FastAPI app with uvicorn.

Usage (from repo root):
    python backend\run_server.py

This loads `app.main:app` and runs uvicorn on 0.0.0.0:8000.
"""

import uvicorn

if __name__ == "__main__":
    # Note: set reload=False in production
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
