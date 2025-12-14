TO RUN TEST SUITE OF FRONTEND:
cd frontend && npm test

TO RUN TEST SUITE OF BACKEND:
cd backend && uv run pytest

TO RUN THE BACKEND SERVER:
cd backend && uv run uvicorn app.main:app --reload

TO RUN THE FRONTEND SERVER:
cd frontend && npm run dev